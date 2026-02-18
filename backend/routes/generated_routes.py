# ============================================================
# backend/routes/generated_routes.py — Dynamic Endpoint Router
# ============================================================
# This is where the MAGIC happens!
#
# When a user deploys a workflow named "my-api", anyone can call:
#   POST /api/generated/my-api
#
# This route handler:
#   1. Looks up the workflow by name in MongoDB.
#   2. Checks that it's deployed.
#   3. Passes it through the workflow engine.
#   4. Returns the result.
#
# It's a single catch-all route that dynamically dispatches
# to the correct workflow — no need to register individual
# Flask routes per workflow.
# ============================================================

from flask import Blueprint, request, jsonify
from backend.models.workflow import WorkflowModel
from backend.workflow_engine import execute_workflow
from backend.extensions import require_db

# Create the blueprint
generated_bp = Blueprint('generated', __name__, url_prefix='/api/generated')


# ============================================================
# POST|GET /api/generated/<workflow_name> — Execute a workflow
# ============================================================
@generated_bp.route('/<workflow_name>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def execute_generated_endpoint(workflow_name):
    """
    Dynamic endpoint that executes a deployed workflow.

    This is the user-facing API endpoint that was "generated"
    by the visual builder. It accepts any HTTP method and passes
    the request data through the workflow engine.

    URL: /api/generated/<workflow_name>

    The workflow_name in the URL must match the workflow's "name"
    field in MongoDB, and the workflow must be in "deployed" status.
    """
    # Check database availability first
    ok, error = require_db()
    if not ok:
        return error

    # Step 1: Look up the deployed workflow
    workflow = WorkflowModel.get_by_name(workflow_name)

    if not workflow:
        return jsonify({
            'error': f'No deployed endpoint found for "{workflow_name}". '
                     f'Make sure the workflow exists and is deployed.',
            'hint': 'Check the dashboard to verify deployment status.'
        }), 404

    # Step 2: Extract request data from the incoming HTTP request
    # Support both JSON body and query parameters
    if request.method in ('POST', 'PUT'):
        request_data = request.get_json(silent=True) or {}
    else:
        request_data = dict(request.args)

    # Step 3: Execute the workflow through the engine
    try:
        result = execute_workflow(workflow, request_data)

        # Step 4: Return the result
        # The result dict has: status_code, body, headers
        response = jsonify(result.get('body', {}))
        response.status_code = result.get('status_code', 200)

        # Apply any custom response headers from the output block
        for key, value in result.get('headers', {}).items():
            response.headers[key] = value

        return response

    except ValueError as e:
        # Validation errors (bad input, unknown block types, cycles)
        return jsonify({
            'error': 'Validation Error',
            'message': str(e),
        }), 400

    except RuntimeError as e:
        # Runtime errors (failed API calls, DB errors)
        return jsonify({
            'error': 'Execution Error',
            'message': str(e),
        }), 502

    except Exception as e:
        # Unexpected errors — log and return generic message
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred while executing the workflow.',
            'details': str(e),
        }), 500
