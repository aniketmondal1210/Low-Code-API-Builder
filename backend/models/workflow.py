# ============================================================
# backend/models/workflow.py — Workflow MongoDB Model
# ============================================================
# This module provides a clean interface for all MongoDB
# operations on workflows. Think of it as a lightweight ORM
# layer — it hides raw pymongo calls behind descriptive methods.
#
# Schema (stored in the "workflows" collection):
# {
#   "_id":          ObjectId,
#   "name":         str,          — unique human-readable name
#   "description":  str,          — optional description
#   "blocks":       [Block],      — list of block definitions
#   "connections":  [Connection], — edges between blocks
#   "status":       str,          — "draft" | "deployed"
#   "created_at":   datetime,
#   "updated_at":   datetime,
# }
#
# Block sub-document:
# {
#   "id":       str,   — unique within the workflow (uuid)
#   "type":     str,   — "input" | "db_query" | "api_call" |
#                        "logic" | "transform" | "output"
#   "label":    str,   — display label on canvas
#   "position": {"x": float, "y": float},
#   "config":   dict,  — type-specific configuration
# }
#
# Connection sub-document:
# {
#   "id":              str,
#   "source_block_id": str,
#   "target_block_id": str,
#   "source_handle":   str,  — e.g. "output"
#   "target_handle":   str,  — e.g. "input"
# }
# ============================================================

from datetime import datetime, timezone
from bson import ObjectId
import backend.extensions as extensions


class WorkflowModel:
    """
    Data-access layer for the 'workflows' MongoDB collection.

    Usage:
        workflow_id = WorkflowModel.create({
            "name": "my-api",
            "blocks": [...],
            "connections": [...]
        })
        workflow = WorkflowModel.get_by_id(workflow_id)

    IMPORTANT — Why we import `backend.extensions` (the module) instead of
    `from backend.extensions import db`:
        In Python, `from X import db` copies the reference at import time.
        Since `db` starts as None and is later reassigned by init_db(),
        the copied reference stays None forever.
        By importing the module, `extensions.db` always reads the CURRENT
        value, which is the live MongoDB database after init_db() runs.
    """

    # ----- Helpers -----

    @staticmethod
    def _collection():
        """Return the pymongo collection handle."""
        if extensions.db is None:
            raise RuntimeError(
                "Database not available. MongoDB connection failed. "
                "Make sure MongoDB is running and MONGO_URI is correctly set."
            )
        return extensions.db['workflows']

    @staticmethod
    def _serialize(doc):
        """
        Convert a MongoDB document to a JSON-safe dict.

        ObjectId → str, so Flask's jsonify can handle it.
        """
        if doc is None:
            return None
        doc['id'] = str(doc.pop('_id'))
        return doc

    # ----- CRUD Operations -----

    @staticmethod
    def create(data):
        """
        Insert a new workflow document.

        Args:
            data (dict): Must include 'name'. Optional: 'description',
                         'blocks', 'connections'.

        Returns:
            str: The inserted document's ID as a string.
        """
        now = datetime.now(timezone.utc)
        document = {
            'name':        data.get('name', 'Untitled Workflow'),
            'description': data.get('description', ''),
            'blocks':      data.get('blocks', []),
            'connections': data.get('connections', []),
            'status':      'draft',       # New workflows start as drafts
            'created_at':  now,
            'updated_at':  now,
        }
        result = WorkflowModel._collection().insert_one(document)
        return str(result.inserted_id)

    @staticmethod
    def get_all():
        """
        Return all workflows, sorted by most recently updated.

        Returns:
            list[dict]: Serialized workflow documents.
        """
        cursor = WorkflowModel._collection().find().sort('updated_at', -1)
        return [WorkflowModel._serialize(doc) for doc in cursor]

    @staticmethod
    def get_by_id(workflow_id):
        """
        Fetch a single workflow by its ID.

        Args:
            workflow_id (str): The document's _id as a string.

        Returns:
            dict | None: Serialized workflow, or None if not found.
        """
        try:
            doc = WorkflowModel._collection().find_one(
                {'_id': ObjectId(workflow_id)}
            )
            return WorkflowModel._serialize(doc)
        except Exception:
            return None

    @staticmethod
    def get_by_name(name):
        """
        Fetch a deployed workflow by its name.

        This is used by the generated endpoint router to look up
        the workflow that backs /api/generated/<workflow_name>.

        Args:
            name (str): Workflow name.

        Returns:
            dict | None
        """
        doc = WorkflowModel._collection().find_one({
            'name': name,
            'status': 'deployed'
        })
        return WorkflowModel._serialize(doc)

    @staticmethod
    def update(workflow_id, data):
        """
        Update a workflow's fields.

        Only updates the fields present in `data`; other fields
        are left untouched (MongoDB $set behaviour).

        Args:
            workflow_id (str): The document's _id.
            data (dict): Fields to update.

        Returns:
            bool: True if a document was modified.
        """
        data['updated_at'] = datetime.now(timezone.utc)
        result = WorkflowModel._collection().update_one(
            {'_id': ObjectId(workflow_id)},
            {'$set': data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(workflow_id):
        """
        Permanently delete a workflow.

        Args:
            workflow_id (str): The document's _id.

        Returns:
            bool: True if a document was deleted.
        """
        result = WorkflowModel._collection().delete_one(
            {'_id': ObjectId(workflow_id)}
        )
        return result.deleted_count > 0

    @staticmethod
    def set_deployed(workflow_id, deployed=True):
        """
        Toggle a workflow's deployment status.

        Args:
            workflow_id (str): The document's _id.
            deployed (bool): True → "deployed", False → "draft".

        Returns:
            bool: True if a document was modified.
        """
        status = 'deployed' if deployed else 'draft'
        return WorkflowModel.update(workflow_id, {'status': status})
