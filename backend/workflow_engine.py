# ============================================================
# backend/workflow_engine.py — Workflow Execution Engine
# ============================================================
# This is the BRAIN of the platform.
#
# When a user calls a deployed endpoint like:
#   POST /api/generated/my-workflow
#
# The system:
#   1. Loads the workflow JSON from MongoDB.
#   2. Passes it to this engine.
#   3. The engine builds a directed execution graph from the
#      blocks and connections.
#   4. Topologically sorts the graph to determine execution order.
#   5. Executes each block in order, passing data through a
#      shared "context" dictionary.
#   6. Returns the final output.
#
# Architecture note:
#   We INTERPRET the workflow JSON at runtime rather than
#   generating and exec-ing Python code. This is:
#   - Safer (no arbitrary code execution)
#   - Easier to debug
#   - More controllable
# ============================================================

import re
import requests as http_requests   # renamed to avoid clash with Flask's request
from collections import deque
import backend.extensions as extensions


# ============================================================
# Block Handler Functions
# ============================================================
# Each handler receives:
#   - block_config (dict): the block's "config" from the workflow JSON
#   - context (dict): shared data passed between blocks
#
# Each handler returns the updated context or a value that gets
# stored under the block's ID in the context.
# ============================================================

def handle_input(block_config, context):
    """
    INPUT BLOCK — Validates and extracts incoming request data.

    Config options:
        - schema: dict describing expected fields and types
          e.g. {"name": "string", "age": "number"}

    The incoming request body is already in context["request_data"].
    This block validates it and makes individual fields available.
    """
    request_data = context.get('request_data', {})
    schema = block_config.get('schema', {})

    # Basic type validation
    errors = []
    for field_name, field_type in schema.items():
        if field_name not in request_data:
            errors.append(f"Missing required field: {field_name}")
            continue

        value = request_data[field_name]
        # Simple type checking
        type_map = {
            'string':  str,
            'number':  (int, float),
            'boolean': bool,
            'array':   list,
            'object':  dict,
        }
        expected = type_map.get(field_type)
        if expected and not isinstance(value, expected):
            errors.append(
                f"Field '{field_name}' expected {field_type}, "
                f"got {type(value).__name__}"
            )

    if errors:
        raise ValueError(f"Input validation failed: {'; '.join(errors)}")

    # Pass validated data forward
    return request_data


def handle_db_query(block_config, context):
    """
    DATABASE QUERY BLOCK — Performs MongoDB operations.

    Config options:
        - collection: str    — MongoDB collection name
        - operation:  str    — "find" | "find_one" | "insert" | "update" | "delete"
        - query:      dict   — MongoDB query filter (supports {{variable}} interpolation)
        - data:       dict   — Document to insert/update fields (for insert/update)
        - limit:      int    — Max documents to return (for find)

    Variable interpolation:
        Values like "{{request_data.name}}" are replaced with
        actual values from the context at runtime.
    """
    collection_name = block_config.get('collection', 'default')
    operation = block_config.get('operation', 'find')
    query = _interpolate_values(block_config.get('query', {}), context)
    data = _interpolate_values(block_config.get('data', {}), context)
    limit = block_config.get('limit', 100)

    if extensions.db is None:
        return {'error': 'Database not available', 'results': []}
    collection = extensions.db[collection_name]

    if operation == 'find':
        cursor = collection.find(query).limit(limit)
        # Convert ObjectIds to strings for JSON serialization
        results = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            results.append(doc)
        return results

    elif operation == 'find_one':
        doc = collection.find_one(query)
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc

    elif operation == 'insert':
        result = collection.insert_one(data)
        return {'inserted_id': str(result.inserted_id)}

    elif operation == 'update':
        result = collection.update_many(query, {'$set': data})
        return {'modified_count': result.modified_count}

    elif operation == 'delete':
        result = collection.delete_many(query)
        return {'deleted_count': result.deleted_count}

    else:
        raise ValueError(f"Unknown DB operation: {operation}")


def handle_api_call(block_config, context):
    """
    EXTERNAL API CALL BLOCK — Makes HTTP requests to external services.

    Config options:
        - url:     str   — Target URL (supports {{variable}} interpolation)
        - method:  str   — "GET" | "POST" | "PUT" | "DELETE"
        - headers: dict  — Request headers
        - body:    dict  — Request body (for POST/PUT)
        - timeout: int   — Timeout in seconds (default: 30)
    """
    url = _interpolate_string(block_config.get('url', ''), context)
    method = block_config.get('method', 'GET').upper()
    headers = _interpolate_values(block_config.get('headers', {}), context)
    body = _interpolate_values(block_config.get('body', {}), context)
    timeout = block_config.get('timeout', 30)

    try:
        response = http_requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body if method in ('POST', 'PUT', 'PATCH') else None,
            params=body if method == 'GET' else None,
            timeout=timeout
        )
        # Try to parse as JSON, fall back to text
        try:
            return response.json()
        except ValueError:
            return {'response_text': response.text, 'status_code': response.status_code}

    except http_requests.RequestException as e:
        raise RuntimeError(f"External API call failed: {str(e)}")


def handle_logic(block_config, context):
    """
    LOGIC / CONDITION BLOCK — Evaluates simple conditions.

    Config options:
        - condition: str — A simple condition expression, e.g.:
              "{{request_data.age}} > 18"
              "{{db_result.status}} == 'active'"
        - true_value:  any — Value to return if condition is true
        - false_value: any — Value to return if condition is false

    Security note:
        We do NOT use eval(). Instead, we parse the condition manually
        to prevent arbitrary code execution.
    """
    condition_str = _interpolate_string(
        block_config.get('condition', 'true'), context
    )
    true_value = block_config.get('true_value', True)
    false_value = block_config.get('false_value', False)

    result = _safe_evaluate_condition(condition_str)

    if result:
        return _interpolate_values(true_value, context) if isinstance(true_value, dict) else true_value
    else:
        return _interpolate_values(false_value, context) if isinstance(false_value, dict) else false_value


def handle_transform(block_config, context):
    """
    TRANSFORMATION BLOCK — Maps, renames, and filters data fields.

    Config options:
        - operations: list of transform operations:
            [
              {"type": "rename", "from": "old_name", "to": "new_name"},
              {"type": "pick",   "fields": ["name", "email"]},
              {"type": "set",    "field": "status", "value": "processed"},
              {"type": "delete", "field": "password"},
              {"type": "template", "field": "greeting",
               "value": "Hello, {{request_data.name}}!"}
            ]
        - input_ref: str — Context key to read data from
                          (default: previous block's output)
    """
    operations = block_config.get('operations', [])
    input_ref = block_config.get('input_ref', None)

    # Determine the source data
    if input_ref:
        data = _resolve_context_path(input_ref, context)
        if isinstance(data, dict):
            data = dict(data)  # shallow copy
        elif isinstance(data, list):
            data = list(data)
    else:
        # Use the most recent block output from context
        data = context.get('_last_output', {})
        if isinstance(data, dict):
            data = dict(data)

    # Apply each operation in sequence
    for op in operations:
        op_type = op.get('type', '')

        if op_type == 'rename' and isinstance(data, dict):
            old = op.get('from', '')
            new = op.get('to', '')
            if old in data:
                data[new] = data.pop(old)

        elif op_type == 'pick' and isinstance(data, dict):
            fields = op.get('fields', [])
            data = {k: v for k, v in data.items() if k in fields}

        elif op_type == 'set' and isinstance(data, dict):
            field = op.get('field', '')
            value = op.get('value', '')
            if isinstance(value, str) and '{{' in value:
                value = _interpolate_string(value, context)
            data[field] = value

        elif op_type == 'delete' and isinstance(data, dict):
            field = op.get('field', '')
            data.pop(field, None)

        elif op_type == 'template' and isinstance(data, dict):
            field = op.get('field', '')
            value = _interpolate_string(op.get('value', ''), context)
            data[field] = value

    return data


def handle_output(block_config, context):
    """
    OUTPUT BLOCK — Formats the final API response.

    Config options:
        - status_code: int  — HTTP status code (default: 200)
        - body:        dict — Response body template (supports {{variable}})
        - headers:     dict — Additional response headers
    """
    status_code = block_config.get('status_code', 200)
    body = block_config.get('body', {})
    headers = block_config.get('headers', {})

    # Interpolate the body template with context values
    resolved_body = _interpolate_values(body, context)

    return {
        'status_code': status_code,
        'body': resolved_body,
        'headers': headers,
    }


# ============================================================
# Handler Registry
# ============================================================
# Maps block type strings to their handler functions.
# When adding a new block type, just add an entry here.
# ============================================================

BLOCK_HANDLERS = {
    'input':     handle_input,
    'db_query':  handle_db_query,
    'api_call':  handle_api_call,
    'logic':     handle_logic,
    'transform': handle_transform,
    'output':    handle_output,
}


# ============================================================
# Execution Graph Builder
# ============================================================

def build_execution_order(blocks, connections):
    """
    Build a topologically sorted execution order from blocks
    and connections.

    This implements Kahn's algorithm for topological sorting:
    1. Count incoming edges for each block.
    2. Start with blocks that have zero incoming edges.
    3. Process each block, reducing in-degree of its neighbours.
    4. Repeat until all blocks are processed.

    Args:
        blocks (list[dict]): Block definitions from the workflow.
        connections (list[dict]): Connection definitions.

    Returns:
        list[dict]: Blocks in execution order.

    Raises:
        ValueError: If the graph has a cycle (impossible to sort).
    """
    # Build adjacency list and in-degree count
    block_map = {b['id']: b for b in blocks}
    in_degree = {b['id']: 0 for b in blocks}
    adjacency = {b['id']: [] for b in blocks}

    for conn in connections:
        src = conn['source_block_id']
        tgt = conn['target_block_id']
        adjacency[src].append(tgt)
        in_degree[tgt] = in_degree.get(tgt, 0) + 1

    # Start with blocks that have no incoming connections
    queue = deque(
        [bid for bid, degree in in_degree.items() if degree == 0]
    )
    sorted_order = []

    while queue:
        current = queue.popleft()
        sorted_order.append(block_map[current])

        for neighbour in adjacency[current]:
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    # If we couldn't sort all blocks, there's a cycle
    if len(sorted_order) != len(blocks):
        raise ValueError(
            "Workflow contains a cycle — blocks cannot be executed "
            "in a valid order. Please check your connections."
        )

    return sorted_order


# ============================================================
# Main Execution Function
# ============================================================

def execute_workflow(workflow, request_data=None):
    """
    Execute a complete workflow against incoming request data.

    This is the main entry point called by the generated endpoint
    router when a user hits /api/generated/<workflow_name>.

    Args:
        workflow (dict): Full workflow document from MongoDB.
        request_data (dict): The incoming HTTP request body.

    Returns:
        dict: {
            "status_code": int,
            "body": any,
            "headers": dict
        }
    """
    blocks = workflow.get('blocks', [])
    connections = workflow.get('connections', [])

    if not blocks:
        return {
            'status_code': 200,
            'body': {'message': 'Empty workflow — no blocks to execute'},
            'headers': {},
        }

    # Step 1: Determine execution order
    execution_order = build_execution_order(blocks, connections)

    # Step 2: Initialize shared context
    # The context is a dict that all blocks can read from and write to.
    # Each block's output is stored under its block ID.
    context = {
        'request_data': request_data or {},
        '_last_output': None,
    }

    # Step 3: Execute each block in order
    final_output = None

    for block in execution_order:
        block_type = block.get('type', '')
        block_id = block.get('id', '')
        block_config = block.get('config', {})

        handler = BLOCK_HANDLERS.get(block_type)
        if handler is None:
            raise ValueError(f"Unknown block type: {block_type}")

        # Execute the handler
        result = handler(block_config, context)

        # Store result in context so downstream blocks can access it
        context[block_id] = result
        context['_last_output'] = result

        # If this is an output block, capture its result
        if block_type == 'output':
            final_output = result

    # If no output block was found, wrap the last result
    if final_output is None:
        final_output = {
            'status_code': 200,
            'body': context.get('_last_output', {}),
            'headers': {},
        }

    return final_output


# ============================================================
# Helper / Utility Functions
# ============================================================

def _interpolate_string(template, context):
    """
    Replace {{path.to.value}} placeholders in a string with
    actual values from the context.

    Example:
        _interpolate_string("Hello, {{request_data.name}}!", context)
        → "Hello, Alice!"
    """
    if not isinstance(template, str):
        return template

    def replacer(match):
        path = match.group(1).strip()
        value = _resolve_context_path(path, context)
        return str(value) if value is not None else ''

    return re.sub(r'\{\{(.+?)\}\}', replacer, template)


def _interpolate_values(obj, context):
    """
    Recursively interpolate {{...}} placeholders in a dict/list.

    Walks through all values in a nested structure and replaces
    any string containing {{...}} with the resolved value.
    """
    if isinstance(obj, str):
        # If the entire string is a single placeholder, return the raw value
        # (preserves type — e.g. returns int instead of "123")
        match = re.fullmatch(r'\{\{(.+?)\}\}', obj.strip())
        if match:
            return _resolve_context_path(match.group(1).strip(), context)
        return _interpolate_string(obj, context)

    elif isinstance(obj, dict):
        return {k: _interpolate_values(v, context) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [_interpolate_values(item, context) for item in obj]

    return obj


def _resolve_context_path(path, context):
    """
    Resolve a dot-notation path against the context dict.

    Example:
        context = {"request_data": {"user": {"name": "Alice"}}}
        _resolve_context_path("request_data.user.name", context)
        → "Alice"
    """
    parts = path.split('.')
    current = context

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None

    return current


def _safe_evaluate_condition(condition_str):
    """
    Safely evaluate a simple comparison condition.

    Supports: ==, !=, >, <, >=, <=, 'true', 'false'

    We do NOT use eval() — instead we parse the condition
    string manually for safety.

    Examples:
        "42 > 18"        → True
        "active == active" → True
        "true"           → True
    """
    condition_str = condition_str.strip()

    # Handle bare boolean strings
    if condition_str.lower() == 'true':
        return True
    if condition_str.lower() == 'false':
        return False

    # Try to match a comparison pattern: left OPERATOR right
    operators = ['==', '!=', '>=', '<=', '>', '<']
    for op in operators:
        if op in condition_str:
            parts = condition_str.split(op, 1)
            if len(parts) == 2:
                left = _parse_value(parts[0].strip())
                right = _parse_value(parts[1].strip())

                if op == '==':  return left == right
                if op == '!=':  return left != right
                if op == '>':   return left > right
                if op == '<':   return left < right
                if op == '>=':  return left >= right
                if op == '<=':  return left <= right

    # Default: truthy check
    return bool(condition_str)


def _parse_value(val_str):
    """
    Parse a string into its Python equivalent.

    "42"     → 42
    "3.14"   → 3.14
    "'hello'" → "hello"
    "true"    → True
    "null"    → None
    "hello"   → "hello"
    """
    # Remove surrounding quotes
    if (val_str.startswith("'") and val_str.endswith("'")) or \
       (val_str.startswith('"') and val_str.endswith('"')):
        return val_str[1:-1]

    # Boolean
    if val_str.lower() == 'true':
        return True
    if val_str.lower() == 'false':
        return False

    # Null
    if val_str.lower() in ('null', 'none'):
        return None

    # Number
    try:
        if '.' in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        pass

    # Fall back to string
    return val_str
