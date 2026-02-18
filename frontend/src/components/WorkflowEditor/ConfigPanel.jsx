// ============================================================
// WorkflowEditor/ConfigPanel.jsx — Node Configuration Panel
// ============================================================
// When a node is selected on the canvas, this panel slides in
// from the right, showing editable form fields for that block's
// configuration.
//
// Each block type has its own config form:
//   - Input:     Schema definition (field names + types)
//   - DB Query:  Collection, operation, query, data
//   - API Call:  URL, method, headers, body
//   - Logic:     Condition, true/false values
//   - Transform: List of operations
//   - Output:    Status code, response body
// ============================================================

import { useState, useEffect } from 'react';
import { BLOCK_TYPES } from './nodes/CustomNodes';
import './ConfigPanel.css';


function ConfigPanel({ selectedNode, onUpdateConfig, onClose }) {
    // Local state for the config being edited
    const [config, setConfig] = useState({});

    // Sync local state when a different node is selected
    useEffect(() => {
        if (selectedNode) {
            setConfig(selectedNode.data?.config || {});
        }
    }, [selectedNode]);

    // No node selected → don't render
    if (!selectedNode) return null;

    const blockMeta = BLOCK_TYPES[selectedNode.data?.type] || {};

    /**
     * Update a config field and notify the parent.
     */
    const updateField = (field, value) => {
        const updated = { ...config, [field]: value };
        setConfig(updated);
        onUpdateConfig(selectedNode.id, updated);
    };

    /**
     * Try to parse a JSON string, returning the original string on failure.
     */
    const parseJSON = (str) => {
        try { return JSON.parse(str); }
        catch { return str; }
    };

    /**
     * Safely stringify a value for display in a textarea.
     */
    const toJSON = (val) => {
        if (typeof val === 'string') return val;
        try { return JSON.stringify(val, null, 2); }
        catch { return String(val); }
    };


    // ============================================================
    // Config forms for each block type
    // ============================================================

    const renderInputConfig = () => (
        <>
            <div className="config-field">
                <label className="label">Request Schema (JSON)</label>
                <textarea
                    className="input"
                    rows={6}
                    value={toJSON(config.schema)}
                    onChange={(e) => updateField('schema', parseJSON(e.target.value))}
                    placeholder='{"name": "string", "age": "number"}'
                />
                <p className="config-help">
                    Define expected fields and their types. Supported types:
                    string, number, boolean, array, object.
                </p>
            </div>
        </>
    );

    const renderDbQueryConfig = () => (
        <>
            <div className="config-field">
                <label className="label">Collection Name</label>
                <input
                    className="input"
                    value={config.collection || ''}
                    onChange={(e) => updateField('collection', e.target.value)}
                    placeholder="users"
                />
            </div>
            <div className="config-field">
                <label className="label">Operation</label>
                <select
                    className="select"
                    value={config.operation || 'find'}
                    onChange={(e) => updateField('operation', e.target.value)}
                >
                    <option value="find">Find (multiple)</option>
                    <option value="find_one">Find One</option>
                    <option value="insert">Insert</option>
                    <option value="update">Update</option>
                    <option value="delete">Delete</option>
                </select>
            </div>
            <div className="config-field">
                <label className="label">Query Filter (JSON)</label>
                <textarea
                    className="input"
                    rows={3}
                    value={toJSON(config.query)}
                    onChange={(e) => updateField('query', parseJSON(e.target.value))}
                    placeholder='{"status": "active"}'
                />
                <p className="config-help">
                    Use {'{{variable}}'} for dynamic values, e.g.{' '}
                    {'{"name": "{{request_data.name}}"}'}.
                </p>
            </div>
            {['insert', 'update'].includes(config.operation) && (
                <div className="config-field">
                    <label className="label">Data (JSON)</label>
                    <textarea
                        className="input"
                        rows={3}
                        value={toJSON(config.data)}
                        onChange={(e) => updateField('data', parseJSON(e.target.value))}
                        placeholder='{"name": "John", "age": 30}'
                    />
                </div>
            )}
            {['find'].includes(config.operation) && (
                <div className="config-field">
                    <label className="label">Limit</label>
                    <input
                        className="input"
                        type="number"
                        value={config.limit || 100}
                        onChange={(e) => updateField('limit', parseInt(e.target.value) || 100)}
                    />
                </div>
            )}
        </>
    );

    const renderApiCallConfig = () => (
        <>
            <div className="config-field">
                <label className="label">URL</label>
                <input
                    className="input"
                    value={config.url || ''}
                    onChange={(e) => updateField('url', e.target.value)}
                    placeholder="https://api.example.com/data"
                />
            </div>
            <div className="config-field">
                <label className="label">Method</label>
                <select
                    className="select"
                    value={config.method || 'GET'}
                    onChange={(e) => updateField('method', e.target.value)}
                >
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                    <option value="PUT">PUT</option>
                    <option value="DELETE">DELETE</option>
                    <option value="PATCH">PATCH</option>
                </select>
            </div>
            <div className="config-field">
                <label className="label">Headers (JSON)</label>
                <textarea
                    className="input"
                    rows={3}
                    value={toJSON(config.headers)}
                    onChange={(e) => updateField('headers', parseJSON(e.target.value))}
                    placeholder='{"Authorization": "Bearer token"}'
                />
            </div>
            <div className="config-field">
                <label className="label">Body (JSON)</label>
                <textarea
                    className="input"
                    rows={3}
                    value={toJSON(config.body)}
                    onChange={(e) => updateField('body', parseJSON(e.target.value))}
                    placeholder='{"key": "value"}'
                />
            </div>
            <div className="config-field">
                <label className="label">Timeout (seconds)</label>
                <input
                    className="input"
                    type="number"
                    value={config.timeout || 30}
                    onChange={(e) => updateField('timeout', parseInt(e.target.value) || 30)}
                />
            </div>
        </>
    );

    const renderLogicConfig = () => (
        <>
            <div className="config-field">
                <label className="label">Condition</label>
                <input
                    className="input"
                    value={config.condition || ''}
                    onChange={(e) => updateField('condition', e.target.value)}
                    placeholder="{{request_data.age}} > 18"
                />
                <p className="config-help">
                    Simple comparison: ==, !=, &gt;, &lt;, &gt;=, &lt;=.
                    Use {'{{variable}}'} placeholders.
                </p>
            </div>
            <div className="config-field">
                <label className="label">Value if True (JSON)</label>
                <textarea
                    className="input"
                    rows={3}
                    value={toJSON(config.true_value)}
                    onChange={(e) => updateField('true_value', parseJSON(e.target.value))}
                />
            </div>
            <div className="config-field">
                <label className="label">Value if False (JSON)</label>
                <textarea
                    className="input"
                    rows={3}
                    value={toJSON(config.false_value)}
                    onChange={(e) => updateField('false_value', parseJSON(e.target.value))}
                />
            </div>
        </>
    );

    const renderTransformConfig = () => (
        <>
            <div className="config-field">
                <label className="label">Operations (JSON array)</label>
                <textarea
                    className="input"
                    rows={8}
                    value={toJSON(config.operations)}
                    onChange={(e) => updateField('operations', parseJSON(e.target.value))}
                    placeholder={`[
  {"type": "rename", "from": "old", "to": "new"},
  {"type": "set", "field": "status", "value": "done"},
  {"type": "pick", "fields": ["name", "email"]},
  {"type": "delete", "field": "password"}
]`}
                />
                <p className="config-help">
                    Types: rename, pick, set, delete, template.
                </p>
            </div>
            <div className="config-field">
                <label className="label">Input Reference (optional)</label>
                <input
                    className="input"
                    value={config.input_ref || ''}
                    onChange={(e) => updateField('input_ref', e.target.value || null)}
                    placeholder="block_id or request_data"
                />
            </div>
        </>
    );

    const renderOutputConfig = () => (
        <>
            <div className="config-field">
                <label className="label">Status Code</label>
                <input
                    className="input"
                    type="number"
                    value={config.status_code || 200}
                    onChange={(e) => updateField('status_code', parseInt(e.target.value) || 200)}
                />
            </div>
            <div className="config-field">
                <label className="label">Response Body (JSON)</label>
                <textarea
                    className="input"
                    rows={6}
                    value={toJSON(config.body)}
                    onChange={(e) => updateField('body', parseJSON(e.target.value))}
                    placeholder='{"message": "Success", "data": "{{_last_output}}"}'
                />
                <p className="config-help">
                    Use {'{{variable}}'} to include dynamic data from previous blocks.
                </p>
            </div>
            <div className="config-field">
                <label className="label">Response Headers (JSON)</label>
                <textarea
                    className="input"
                    rows={3}
                    value={toJSON(config.headers)}
                    onChange={(e) => updateField('headers', parseJSON(e.target.value))}
                    placeholder='{"X-Custom-Header": "value"}'
                />
            </div>
        </>
    );

    // Map block types to their config renderers
    const configRenderers = {
        input: renderInputConfig,
        db_query: renderDbQueryConfig,
        api_call: renderApiCallConfig,
        logic: renderLogicConfig,
        transform: renderTransformConfig,
        output: renderOutputConfig,
    };

    const renderConfig = configRenderers[selectedNode.data?.type];

    return (
        <aside className="config-panel animate-slide-in">
            {/* Panel header */}
            <div className="config-header">
                <div className="config-header-info">
                    <span className="config-header-icon">{blockMeta.icon}</span>
                    <div>
                        <h3 className="config-header-title">{blockMeta.label}</h3>
                        <p className="config-header-desc">{blockMeta.description}</p>
                    </div>
                </div>
                <button className="btn btn-ghost config-close" onClick={onClose}>✕</button>
            </div>

            {/* Node label */}
            <div className="config-body">
                <div className="config-field">
                    <label className="label">Node Label</label>
                    <input
                        className="input"
                        value={selectedNode.data?.label || ''}
                        onChange={(e) => {
                            // Label changes are handled differently — update node data
                            onUpdateConfig(selectedNode.id, config, e.target.value);
                        }}
                        placeholder={blockMeta.label}
                    />
                </div>

                {/* Type-specific config fields */}
                {renderConfig && renderConfig()}
            </div>
        </aside>
    );
}

export default ConfigPanel;
