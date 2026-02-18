// ============================================================
// WorkflowEditor/nodes/CustomNodes.jsx — Custom React Flow Nodes
// ============================================================
// Each block type in the visual editor gets its own custom node
// component. They all share a common structure but have unique
// icons, colors, and descriptions.
//
// React Flow renders these components on the canvas. They receive
// the node's data as props and can include input/output handles
// for connecting to other nodes.
// ============================================================

import { Handle, Position } from '@xyflow/react';
import './CustomNodes.css';


// ============================================================
// Block type metadata — icons, labels, descriptions, defaults
// ============================================================
export const BLOCK_TYPES = {
    input: {
        type: 'input',
        icon: '📥',
        label: 'Input',
        description: 'Define request schema',
        defaultConfig: {
            schema: { name: 'string', value: 'number' },
        },
    },
    db_query: {
        type: 'db_query',
        icon: '🗄️',
        label: 'Database Query',
        description: 'Query MongoDB collection',
        defaultConfig: {
            collection: 'items',
            operation: 'find',
            query: {},
            data: {},
            limit: 100,
        },
    },
    api_call: {
        type: 'api_call',
        icon: '🌐',
        label: 'API Call',
        description: 'Call external API',
        defaultConfig: {
            url: 'https://api.example.com/data',
            method: 'GET',
            headers: {},
            body: {},
            timeout: 30,
        },
    },
    logic: {
        type: 'logic',
        icon: '⚡',
        label: 'Logic',
        description: 'Conditional branching',
        defaultConfig: {
            condition: 'true',
            true_value: { result: 'condition met' },
            false_value: { result: 'condition not met' },
        },
    },
    transform: {
        type: 'transform',
        icon: '🔄',
        label: 'Transform',
        description: 'Transform data fields',
        defaultConfig: {
            operations: [
                { type: 'set', field: 'processed', value: 'true' },
            ],
            input_ref: null,
        },
    },
    output: {
        type: 'output',
        icon: '📤',
        label: 'Output',
        description: 'Define API response',
        defaultConfig: {
            status_code: 200,
            body: { message: 'Success', data: '{{_last_output}}' },
            headers: {},
        },
    },
};


// ============================================================
// Generic custom node component
// ============================================================
// This is used for ALL block types. The visual differences come
// from the data-type attribute on the outer div, which drives
// CSS color changes via CustomNodes.css.
// ============================================================

function CustomNode({ data, selected }) {
    const blockMeta = BLOCK_TYPES[data.type] || BLOCK_TYPES.input;

    return (
        <div
            className={`custom-node ${selected ? 'selected' : ''}`}
            data-type={data.type}
        >
            {/* Input handle — for receiving data from upstream blocks */}
            {data.type !== 'input' && (
                <Handle
                    type="target"
                    position={Position.Top}
                    id="input"
                />
            )}

            {/* Colour-coded header */}
            <div className="node-header">
                <span className="node-icon">{blockMeta.icon}</span>
                <span>{blockMeta.label}</span>
            </div>

            {/* Node body */}
            <div className="node-body">
                <div className="node-label">
                    {data.label || blockMeta.label}
                </div>
                <div className="node-description">
                    {blockMeta.description}
                </div>
            </div>

            {/* Output handle — for sending data to downstream blocks */}
            {data.type !== 'output' && (
                <Handle
                    type="source"
                    position={Position.Bottom}
                    id="output"
                />
            )}
        </div>
    );
}


// ============================================================
// Export individual node types for React Flow's nodeTypes map
// ============================================================
// React Flow requires a mapping from type strings to components.
// We wrap CustomNode so each type gets the correct data.type.
// ============================================================

export const InputNode = (props) => <CustomNode {...props} />;
export const DbQueryNode = (props) => <CustomNode {...props} />;
export const ApiCallNode = (props) => <CustomNode {...props} />;
export const LogicNode = (props) => <CustomNode {...props} />;
export const TransformNode = (props) => <CustomNode {...props} />;
export const OutputNode = (props) => <CustomNode {...props} />;

// The nodeTypes object that React Flow uses
export const nodeTypes = {
    input: InputNode,
    db_query: DbQueryNode,
    api_call: ApiCallNode,
    logic: LogicNode,
    transform: TransformNode,
    output: OutputNode,
};

export default CustomNode;
