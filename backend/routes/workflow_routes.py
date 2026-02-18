# ============================================================
# backend/routes/workflow_routes.py — Workflow CRUD API
# ============================================================
# This blueprint handles all operations on workflows:
#   - List, Create, Read, Update, Delete
#   - Deploy / Undeploy (activate the generated endpoint)
#   - Export generated Flask code
#
# All endpoints are prefixed with /api/workflows
# ============================================================

from flask import Blueprint, request, jsonify
from backend.models.workflow import WorkflowModel
from backend.code_generator import generate_flask_code
from backend.extensions import require_db

# Create the blueprint
workflow_bp = Blueprint('workflows', __name__, url_prefix='/api/workflows')


# ============================================================
# GET /api/workflows — List all workflows
# ============================================================
@workflow_bp.route('', methods=['GET'])
def list_workflows():
    """
    Return all workflows, sorted by most recently updated.

    Response: [{ id, name, description, status, created_at, updated_at }]
    """
    ok, error = require_db()
    if not ok:
        return error
    workflows = WorkflowModel.get_all()
    return jsonify(workflows), 200


# ============================================================
# POST /api/workflows — Create a new workflow
# ============================================================
@workflow_bp.route('', methods=['POST'])
def create_workflow():
    """
    Create a new workflow from the provided JSON body.

    Expected body: { name, description?, blocks?, connections? }
    Response: { id, message }
    """
    ok, error = require_db()
    if not ok:
        return error
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'error': 'Workflow name is required'}), 400

    workflow_id = WorkflowModel.create(data)

    return jsonify({
        'id': workflow_id,
        'message': f'Workflow "{data["name"]}" created successfully'
    }), 201


# ============================================================
# GET /api/workflows/<id> — Get a single workflow
# ============================================================
@workflow_bp.route('/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """
    Return the full workflow document by its ID.

    Includes all blocks, connections, and configuration — this
    is what the frontend editor loads to populate the canvas.
    """
    ok, error = require_db()
    if not ok:
        return error
    workflow = WorkflowModel.get_by_id(workflow_id)

    if not workflow:
        return jsonify({'error': 'Workflow not found'}), 404

    return jsonify(workflow), 200


# ============================================================
# PUT /api/workflows/<id> — Update a workflow
# ============================================================
@workflow_bp.route('/<workflow_id>', methods=['PUT'])
def update_workflow(workflow_id):
    """
    Update an existing workflow.

    The frontend sends the complete blocks/connections arrays
    whenever the user saves the canvas.

    Expected body: { name?, description?, blocks?, connections? }
    """
    ok, error = require_db()
    if not ok:
        return error
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Only allow updating specific fields
    allowed_fields = ['name', 'description', 'blocks', 'connections']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    success = WorkflowModel.update(workflow_id, update_data)

    if not success:
        return jsonify({'error': 'Workflow not found or no changes made'}), 404

    return jsonify({'message': 'Workflow updated successfully'}), 200


# ============================================================
# DELETE /api/workflows/<id> — Delete a workflow
# ============================================================
@workflow_bp.route('/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    """
    Permanently delete a workflow.

    If the workflow is currently deployed, its endpoint will
    also stop working immediately.
    """
    ok, error = require_db()
    if not ok:
        return error
    success = WorkflowModel.delete(workflow_id)

    if not success:
        return jsonify({'error': 'Workflow not found'}), 404

    return jsonify({'message': 'Workflow deleted successfully'}), 200


# ============================================================
# POST /api/workflows/<id>/deploy — Deploy a workflow
# ============================================================
@workflow_bp.route('/<workflow_id>/deploy', methods=['POST'])
def deploy_workflow(workflow_id):
    """
    Activate the generated endpoint for this workflow.

    After deployment, the workflow is accessible at:
        POST /api/generated/<workflow_name>

    Validates that the workflow has at least one block before
    allowing deployment.
    """
    ok, error = require_db()
    if not ok:
        return error
    workflow = WorkflowModel.get_by_id(workflow_id)

    if not workflow:
        return jsonify({'error': 'Workflow not found'}), 404

    if not workflow.get('blocks'):
        return jsonify({
            'error': 'Cannot deploy an empty workflow. '
                     'Add at least one block first.'
        }), 400

    WorkflowModel.set_deployed(workflow_id, deployed=True)

    endpoint_url = f'/api/generated/{workflow["name"]}'
    return jsonify({
        'message': f'Workflow deployed successfully',
        'endpoint': endpoint_url,
    }), 200


# ============================================================
# POST /api/workflows/<id>/undeploy — Undeploy a workflow
# ============================================================
@workflow_bp.route('/<workflow_id>/undeploy', methods=['POST'])
def undeploy_workflow(workflow_id):
    """
    Deactivate the generated endpoint.

    The endpoint URL will return 404 after undeployment.
    """
    ok, error = require_db()
    if not ok:
        return error
    workflow = WorkflowModel.get_by_id(workflow_id)

    if not workflow:
        return jsonify({'error': 'Workflow not found'}), 404

    WorkflowModel.set_deployed(workflow_id, deployed=False)

    return jsonify({
        'message': 'Workflow undeployed successfully'
    }), 200


# ============================================================
# GET /api/workflows/<id>/export — Export generated Flask code
# ============================================================
@workflow_bp.route('/<workflow_id>/export', methods=['GET'])
def export_workflow(workflow_id):
    """
    Generate and return standalone Flask source code for a workflow.

    The user can copy this code into their own project.
    Returns plain text (Python source code).
    """
    ok, error = require_db()
    if not ok:
        return error
    workflow = WorkflowModel.get_by_id(workflow_id)

    if not workflow:
        return jsonify({'error': 'Workflow not found'}), 404

    code = generate_flask_code(workflow)

    return jsonify({
        'code': code,
        'language': 'python',
        'filename': f'{workflow["name"].replace(" ", "_")}_api.py'
    }), 200
