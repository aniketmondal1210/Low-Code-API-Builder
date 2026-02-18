# ============================================================
# backend/routes/docs_routes.py — Auto-Generated API Documentation
# ============================================================
# This blueprint generates a complete OpenAPI 3.0 spec by
# iterating all deployed workflows and stitching together
# their individual specs from the code generator.
#
# The resulting JSON is served at /api/docs/openapi.json,
# which Swagger UI (mounted in app.py) uses to render the
# interactive documentation page.
# ============================================================

from flask import Blueprint, jsonify
from backend.models.workflow import WorkflowModel
from backend.code_generator import generate_openapi_spec
from backend.extensions import require_db, db_available

# Create the blueprint
docs_bp = Blueprint('docs', __name__, url_prefix='/api/docs')


# ============================================================
# GET /api/docs/openapi.json — Full OpenAPI 3.0 specification
# ============================================================
@docs_bp.route('/openapi.json', methods=['GET'])
def get_openapi_spec():
    """
    Generate and return the complete OpenAPI 3.0 specification.

    This dynamically builds the spec every time it's requested,
    so it always reflects the current set of deployed workflows.

    The spec includes:
    - Info section (title, version, description)
    - Server section (base URL)
    - Paths section (one path per deployed workflow)
    - Each path has request/response schemas derived from
      the workflow's input/output blocks.
    """
    # Base OpenAPI 3.0 spec
    spec = {
        'openapi': '3.0.0',
        'info': {
            'title': 'Low-Code API Builder — Generated APIs',
            'version': '1.0.0',
            'description': (
                'This documentation is auto-generated from deployed '
                'workflows. Each endpoint corresponds to a workflow '
                'created in the visual builder.'
            ),
        },
        'servers': [
            {
                'url': 'http://localhost:5000',
                'description': 'Local development server'
            }
        ],
        'paths': {},
        'tags': [
            {
                'name': 'Generated APIs',
                'description': 'Endpoints automatically generated from visual workflows'
            },
            {
                'name': 'Workflow Management',
                'description': 'CRUD operations for managing workflows'
            }
        ]
    }

    # Only include deployed workflow paths if DB is available
    if db_available:
        # Add a path for each deployed workflow
        all_workflows = WorkflowModel.get_all()

        for workflow in all_workflows:
            if workflow.get('status') == 'deployed':
                name = workflow.get('name', 'untitled')
                path = f'/api/generated/{name}'

                # Generate the OpenAPI spec fragment for this workflow
                path_spec = generate_openapi_spec(workflow)
                spec['paths'][path] = path_spec

    # Also document the management API endpoints
    spec['paths'].update(_management_api_docs())

    return jsonify(spec), 200


def _management_api_docs():
    """
    Return OpenAPI path specs for the workflow management API.

    These are the CRUD endpoints for managing workflows themselves
    (not the generated endpoints).
    """
    return {
        '/api/workflows': {
            'get': {
                'summary': 'List all workflows',
                'tags': ['Workflow Management'],
                'responses': {
                    '200': {
                        'description': 'Array of workflow objects',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'array',
                                    'items': {'$ref': '#/components/schemas/Workflow'}
                                }
                            }
                        }
                    }
                }
            },
            'post': {
                'summary': 'Create a new workflow',
                'tags': ['Workflow Management'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'required': ['name'],
                                'properties': {
                                    'name': {'type': 'string'},
                                    'description': {'type': 'string'},
                                    'blocks': {'type': 'array'},
                                    'connections': {'type': 'array'},
                                }
                            }
                        }
                    }
                },
                'responses': {
                    '201': {'description': 'Workflow created'},
                    '400': {'description': 'Validation error'},
                }
            }
        },
        '/api/workflows/{workflow_id}': {
            'get': {
                'summary': 'Get a workflow by ID',
                'tags': ['Workflow Management'],
                'parameters': [
                    {
                        'name': 'workflow_id',
                        'in': 'path',
                        'required': True,
                        'schema': {'type': 'string'}
                    }
                ],
                'responses': {
                    '200': {'description': 'Workflow object'},
                    '404': {'description': 'Not found'},
                }
            },
            'put': {
                'summary': 'Update a workflow',
                'tags': ['Workflow Management'],
                'parameters': [
                    {
                        'name': 'workflow_id',
                        'in': 'path',
                        'required': True,
                        'schema': {'type': 'string'}
                    }
                ],
                'responses': {
                    '200': {'description': 'Updated'},
                    '404': {'description': 'Not found'},
                }
            },
            'delete': {
                'summary': 'Delete a workflow',
                'tags': ['Workflow Management'],
                'parameters': [
                    {
                        'name': 'workflow_id',
                        'in': 'path',
                        'required': True,
                        'schema': {'type': 'string'}
                    }
                ],
                'responses': {
                    '200': {'description': 'Deleted'},
                    '404': {'description': 'Not found'},
                }
            }
        },
        '/api/workflows/{workflow_id}/deploy': {
            'post': {
                'summary': 'Deploy a workflow (activate its endpoint)',
                'tags': ['Workflow Management'],
                'parameters': [
                    {
                        'name': 'workflow_id',
                        'in': 'path',
                        'required': True,
                        'schema': {'type': 'string'}
                    }
                ],
                'responses': {
                    '200': {'description': 'Deployed'},
                    '400': {'description': 'Validation error'},
                    '404': {'description': 'Not found'},
                }
            }
        },
        '/api/workflows/{workflow_id}/undeploy': {
            'post': {
                'summary': 'Undeploy a workflow (deactivate its endpoint)',
                'tags': ['Workflow Management'],
                'parameters': [
                    {
                        'name': 'workflow_id',
                        'in': 'path',
                        'required': True,
                        'schema': {'type': 'string'}
                    }
                ],
                'responses': {
                    '200': {'description': 'Undeployed'},
                    '404': {'description': 'Not found'},
                }
            }
        }
    }
