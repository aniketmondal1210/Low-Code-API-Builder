// ============================================================
// pages/Dashboard.jsx — Workflow Management Dashboard
// ============================================================
// Landing page that shows all saved workflows with:
//   - Status badges (draft / deployed)
//   - Quick actions (edit, deploy/undeploy, delete)
//   - "Create New Workflow" button
//
// This is the first thing users see when they open the app.
// ============================================================

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    getWorkflows,
    createWorkflow,
    deleteWorkflow,
    deployWorkflow,
    undeployWorkflow,
} from '../services/api';
import './Dashboard.css';


function Dashboard() {
    const [workflows, setWorkflows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [creating, setCreating] = useState(false);
    const [toast, setToast] = useState(null);
    const navigate = useNavigate();

    // Fetch workflows on mount
    useEffect(() => { loadWorkflows(); }, []);

    const loadWorkflows = async () => {
        try {
            setLoading(true);
            const data = await getWorkflows();
            setWorkflows(data);
        } catch (err) {
            console.error('Failed to load workflows:', err);
            // Don't show toast on load failure to avoid spamming on startup if DB is down
            // But we could show a global error banner. For now, just log.
        } finally {
            setLoading(false);
        }
    };

    /** Show a temporary toast notification. */
    const showToast = (message, type = 'success') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 5000);
    };

    const handleCreate = async () => {
        if (!newName.trim() || creating) return;
        try {
            setCreating(true);
            const result = await createWorkflow({
                name: newName.trim().replace(/\s+/g, '-').toLowerCase(),
                description: newDesc.trim(),
            });
            setShowCreate(false);
            setNewName('');
            setNewDesc('');
            // Navigate to the editor for the new workflow
            navigate(`/editor/${result.id}`);
        } catch (err) {
            console.error('Failed to create workflow:', err);
            const msg = err.response?.data?.message || err.response?.data?.error || 'Failed to create workflow';
            showToast(msg, 'error');
        } finally {
            setCreating(false);
        }
    };

    const handleDelete = async (id, name) => {
        if (!confirm(`Delete workflow "${name}"? This cannot be undone.`)) return;
        try {
            await deleteWorkflow(id);
            loadWorkflows();
        } catch (err) {
            console.error('Failed to delete workflow:', err);
        }
    };

    const handleToggleDeploy = async (id, currentStatus) => {
        try {
            if (currentStatus === 'deployed') {
                await undeployWorkflow(id);
            } else {
                await deployWorkflow(id);
            }
            loadWorkflows();
        } catch (err) {
            console.error('Failed to toggle deployment:', err);
        }
    };

    return (
        <div className="dashboard">
            {/* Hero Section */}
            <header className="dashboard-hero">
                <div className="hero-content">
                    <h1 className="hero-title">
                        <span className="gradient-text">API Builder</span> Platform
                    </h1>
                    <p className="hero-subtitle">
                        Design, build, and deploy APIs visually — no boilerplate needed.
                    </p>
                    <button
                        className="btn btn-primary btn-lg"
                        onClick={() => setShowCreate(true)}
                    >
                        ✨ Create New Workflow
                    </button>
                </div>
                <div className="hero-glow" />
            </header>

            {/* Quick Stats */}
            <div className="dashboard-stats">
                <div className="stat-card glass-card">
                    <div className="stat-number">{workflows.length}</div>
                    <div className="stat-label">Total Workflows</div>
                </div>
                <div className="stat-card glass-card">
                    <div className="stat-number stat-deployed">
                        {workflows.filter((w) => w.status === 'deployed').length}
                    </div>
                    <div className="stat-label">Deployed</div>
                </div>
                <div className="stat-card glass-card">
                    <div className="stat-number stat-draft">
                        {workflows.filter((w) => w.status === 'draft').length}
                    </div>
                    <div className="stat-label">Drafts</div>
                </div>
            </div>

            {/* Create Workflow Modal */}
            {showCreate && (
                <div className="modal-overlay" onClick={() => setShowCreate(false)}>
                    <div
                        className="modal glass-card animate-fade-in"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h2 className="modal-title">Create New Workflow</h2>
                        <div className="config-field">
                            <label className="label">Workflow Name</label>
                            <input
                                className="input"
                                value={newName}
                                onChange={(e) => setNewName(e.target.value)}
                                placeholder="my-awesome-api"
                                autoFocus
                                disabled={creating}
                                onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
                            />
                            <p className="config-help">
                                This becomes the endpoint URL: /api/generated/my-awesome-api
                            </p>
                        </div>
                        <div className="config-field">
                            <label className="label">Description (optional)</label>
                            <textarea
                                className="input"
                                value={newDesc}
                                onChange={(e) => setNewDesc(e.target.value)}
                                placeholder="What does this API do?"
                                rows={3}
                                disabled={creating}
                            />
                        </div>
                        <div className="modal-actions">
                            <button
                                className="btn btn-secondary"
                                onClick={() => setShowCreate(false)}
                                disabled={creating}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={handleCreate}
                                disabled={creating}
                            >
                                {creating ? (
                                    <>
                                        <span className="btn-spinner" />
                                        Creating...
                                    </>
                                ) : (
                                    'Create & Open Editor'
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Workflow list */}
            <section className="dashboard-section">
                <h2 className="section-title">Your Workflows</h2>

                {loading ? (
                    <div className="loading-state">
                        <div className="loading-spinner" />
                        <p>Loading workflows...</p>
                    </div>
                ) : workflows.length === 0 ? (
                    <div className="empty-state glass-card">
                        <div className="empty-icon">🛠️</div>
                        <h3>No workflows yet</h3>
                        <p>Create your first workflow to get started building APIs visually.</p>
                        <button
                            className="btn btn-primary"
                            onClick={() => setShowCreate(true)}
                        >
                            ✨ Create First Workflow
                        </button>
                    </div>
                ) : (
                    <div className="workflow-grid">
                        {workflows.map((wf, index) => (
                            <div
                                key={wf.id}
                                className="workflow-card glass-card animate-fade-in"
                                style={{ animationDelay: `${index * 60}ms` }}
                            >
                                <div className="wf-card-header">
                                    <h3 className="wf-card-name">{wf.name}</h3>
                                    <span className={`badge badge-${wf.status}`}>
                                        {wf.status === 'deployed' ? '● Live' : '○ Draft'}
                                    </span>
                                </div>

                                {wf.description && (
                                    <p className="wf-card-desc">{wf.description}</p>
                                )}

                                {wf.status === 'deployed' && (
                                    <div className="wf-card-endpoint">
                                        <code>/api/generated/{wf.name}</code>
                                    </div>
                                )}

                                <div className="wf-card-meta">
                                    <span>
                                        {wf.blocks?.length || 0} block{(wf.blocks?.length || 0) !== 1 ? 's' : ''}
                                    </span>
                                    <span>•</span>
                                    <span>
                                        {wf.connections?.length || 0} connection{(wf.connections?.length || 0) !== 1 ? 's' : ''}
                                    </span>
                                </div>

                                <div className="wf-card-actions">
                                    <button
                                        className="btn btn-primary btn-sm"
                                        onClick={() => navigate(`/editor/${wf.id}`)}
                                    >
                                        ✏️ Edit
                                    </button>
                                    <button
                                        className={`btn btn-sm ${wf.status === 'deployed' ? 'btn-danger' : 'btn-success'}`}
                                        onClick={() => handleToggleDeploy(wf.id, wf.status)}
                                    >
                                        {wf.status === 'deployed' ? '⏸ Undeploy' : '🚀 Deploy'}
                                    </button>
                                    <button
                                        className="btn btn-ghost btn-sm"
                                        onClick={() => handleDelete(wf.id, wf.name)}
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>
            {/* Toast notification */}
            {toast && (
                <div className={`toast toast-${toast.type}`}>
                    {toast.message}
                </div>
            )}
        </div>
    );
}

export default Dashboard;
