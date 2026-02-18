// ============================================================
// services/api.js — Backend API Client
// ============================================================
// Centralised Axios instance + wrapper functions for every
// backend endpoint. All API calls go through here so we can
// easily change the base URL, add auth headers, etc.
// ============================================================

import axios from 'axios';

// Create a pre-configured Axios instance
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,   // 30-second timeout
});


// ============================================================
// Workflow CRUD
// ============================================================

/** Fetch all workflows (sorted by most recently updated). */
export const getWorkflows = () =>
  api.get('/workflows').then(res => res.data);

/** Fetch a single workflow by its ID. */
export const getWorkflow = (id) =>
  api.get(`/workflows/${id}`).then(res => res.data);

/** Create a new workflow. */
export const createWorkflow = (data) =>
  api.post('/workflows', data).then(res => res.data);

/** Update an existing workflow. */
export const updateWorkflow = (id, data) =>
  api.put(`/workflows/${id}`, data).then(res => res.data);

/** Delete a workflow. */
export const deleteWorkflow = (id) =>
  api.delete(`/workflows/${id}`).then(res => res.data);


// ============================================================
// Deployment
// ============================================================

/** Deploy (activate) a workflow's endpoint. */
export const deployWorkflow = (id) =>
  api.post(`/workflows/${id}/deploy`).then(res => res.data);

/** Undeploy (deactivate) a workflow's endpoint. */
export const undeployWorkflow = (id) =>
  api.post(`/workflows/${id}/undeploy`).then(res => res.data);


// ============================================================
// Code Export
// ============================================================

/** Get the generated Flask code for a workflow. */
export const exportWorkflowCode = (id) =>
  api.get(`/workflows/${id}/export`).then(res => res.data);


// ============================================================
// Generated API Testing
// ============================================================

/** Call a deployed generated endpoint for testing. */
export const testGeneratedEndpoint = (workflowName, data = {}) =>
  api.post(`/generated/${workflowName}`, data).then(res => res.data);


export default api;
