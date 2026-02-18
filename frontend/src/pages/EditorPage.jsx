// ============================================================
// pages/EditorPage.jsx — Full-Screen Workflow Editor Page
// ============================================================
// Loads a workflow by ID from the URL params and renders the
// WorkflowEditor component. Handles save, deploy, undeploy,
// and export actions by calling the API service.
// ============================================================

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import WorkflowEditor from '../components/WorkflowEditor/WorkflowEditor';
import {
    getWorkflow,
    updateWorkflow,
    deployWorkflow,
    undeployWorkflow,
    exportWorkflowCode,
} from '../services/api';
import './EditorPage.css';


function EditorPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [workflow, setWorkflow] = useState(null);
    const [loading, setLoading] = useState(true);
    const [toast, setToast] = useState(null);

    // Load the workflow on mount
    useEffect(() => {
        loadWorkflow();
    }, [id]);

    const loadWorkflow = async () => {
        try {
            setLoading(true);
            const data = await getWorkflow(id);
            setWorkflow(data);
        } catch (err) {
            console.error('Failed to load workflow:', err);
            showToast('Failed to load workflow', 'error');
        } finally {
            setLoading(false);
        }
    };

    /** Show a temporary toast notification. */
    const showToast = (message, type = 'success') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3000);
    };

    /** Save the canvas state to MongoDB. */
    const handleSave = async ({ blocks, connections }) => {
        try {
            await updateWorkflow(id, { blocks, connections });
            setWorkflow((prev) => ({ ...prev, blocks, connections }));
            showToast('Workflow saved successfully! 💾');
        } catch (err) {
            console.error('Save failed:', err);
            showToast('Failed to save workflow', 'error');
        }
    };

    /** Deploy the workflow (activate its endpoint). */
    const handleDeploy = async () => {
        try {
            const result = await deployWorkflow(id);
            setWorkflow((prev) => ({ ...prev, status: 'deployed' }));
            showToast(`Deployed! Endpoint: ${result.endpoint} 🚀`);
        } catch (err) {
            const msg = err.response?.data?.error || 'Deployment failed';
            showToast(msg, 'error');
        }
    };

    /** Undeploy the workflow. */
    const handleUndeploy = async () => {
        try {
            await undeployWorkflow(id);
            setWorkflow((prev) => ({ ...prev, status: 'draft' }));
            showToast('Workflow undeployed ⏸');
        } catch (err) {
            showToast('Failed to undeploy', 'error');
        }
    };

    /** Export generated Flask code. */
    const handleExport = async () => {
        try {
            const result = await exportWorkflowCode(id);
            // Open a new window with the generated code
            const win = window.open('', '_blank');
            win.document.write(`<pre style="background:#0a0a0f;color:#f1f1f3;padding:24px;font-family:monospace;white-space:pre-wrap;">${escapeHtml(result.code)}</pre>`);
            win.document.title = result.filename;
            showToast('Code exported! Check the new tab 📄');
        } catch (err) {
            showToast('Failed to export code', 'error');
        }
    };

    /** Escape HTML for safe rendering. */
    const escapeHtml = (str) =>
        str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // --- Render ---

    if (loading) {
        return (
            <div className="editor-loading">
                <div className="loading-spinner" />
                <p>Loading workflow...</p>
            </div>
        );
    }

    if (!workflow) {
        return (
            <div className="editor-error">
                <h2>Workflow not found</h2>
                <p>The workflow you're looking for doesn't exist.</p>
                <button className="btn btn-primary" onClick={() => navigate('/')}>
                    Back to Dashboard
                </button>
            </div>
        );
    }

    return (
        <div className="editor-page">
            {/* Navigation bar */}
            <nav className="editor-nav">
                <button className="btn btn-ghost" onClick={() => navigate('/')}>
                    ← Dashboard
                </button>
                <div className="nav-links">
                    <button className="btn btn-ghost" onClick={() => navigate('/docs')}>
                        📚 API Docs
                    </button>
                </div>
            </nav>

            {/* The visual editor */}
            <WorkflowEditor
                workflow={workflow}
                onSave={handleSave}
                onDeploy={handleDeploy}
                onUndeploy={handleUndeploy}
                onExport={handleExport}
            />

            {/* Toast notification */}
            {toast && (
                <div className={`toast toast-${toast.type} animate-fade-in`}>
                    {toast.message}
                </div>
            )}
        </div>
    );
}

export default EditorPage;
