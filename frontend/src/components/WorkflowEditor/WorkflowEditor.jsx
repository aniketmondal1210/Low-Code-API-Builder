// ============================================================
// WorkflowEditor/WorkflowEditor.jsx — Main Canvas Component
// ============================================================
// This is the heart of the visual builder. It renders the
// React Flow canvas where users:
//   1. Drag blocks from the sidebar onto the canvas.
//   2. Connect blocks with edges.
//   3. Select blocks to edit their config in the right panel.
//
// React Flow handles all the heavy lifting — panning, zooming,
// node positioning, edge routing, and selection.
// ============================================================

import { useState, useCallback, useRef } from 'react';
import {
    ReactFlow,
    Controls,
    MiniMap,
    Background,
    addEdge,
    useNodesState,
    useEdgesState,
    MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { nodeTypes, BLOCK_TYPES } from './nodes/CustomNodes';
import Sidebar from './Sidebar';
import ConfigPanel from './ConfigPanel';
import './WorkflowEditor.css';


// ============================================================
// Helper: Generate a unique ID for new nodes/edges
// ============================================================
let idCounter = 0;
const generateId = () => `block_${Date.now()}_${idCounter++}`;


function WorkflowEditor({ workflow, onSave, onDeploy, onUndeploy, onExport }) {
    // --- React Flow state ---
    // nodes = blocks on the canvas
    // edges = connections between blocks
    const [nodes, setNodes, onNodesChange] = useNodesState(
        workflow?.blocks?.map(blockToNode) || []
    );
    const [edges, setEdges, onEdgesChange] = useEdgesState(
        workflow?.connections?.map(connToEdge) || []
    );

    // --- UI state ---
    const [selectedNode, setSelectedNode] = useState(null);
    const reactFlowWrapper = useRef(null);
    const [reactFlowInstance, setReactFlowInstance] = useState(null);


    // ============================================================
    // Convert between our workflow format and React Flow format
    // ============================================================

    /** Convert a workflow block to a React Flow node. */
    function blockToNode(block) {
        return {
            id: block.id,
            type: block.type,
            position: block.position || { x: 250, y: 100 },
            data: {
                type: block.type,
                label: block.label || BLOCK_TYPES[block.type]?.label || 'Block',
                config: block.config || BLOCK_TYPES[block.type]?.defaultConfig || {},
            },
        };
    }

    /** Convert a workflow connection to a React Flow edge. */
    function connToEdge(conn) {
        return {
            id: conn.id || `edge_${conn.source_block_id}_${conn.target_block_id}`,
            source: conn.source_block_id,
            target: conn.target_block_id,
            sourceHandle: conn.source_handle || 'output',
            targetHandle: conn.target_handle || 'input',
            animated: true,
            style: { stroke: '#6366f1', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#6366f1' },
        };
    }

    /** Convert React Flow nodes back to workflow blocks. */
    function nodesToBlocks(rfNodes) {
        return rfNodes.map((node) => ({
            id: node.id,
            type: node.data.type || node.type,
            label: node.data.label,
            position: node.position,
            config: node.data.config,
        }));
    }

    /** Convert React Flow edges back to workflow connections. */
    function edgesToConnections(rfEdges) {
        return rfEdges.map((edge) => ({
            id: edge.id,
            source_block_id: edge.source,
            target_block_id: edge.target,
            source_handle: edge.sourceHandle || 'output',
            target_handle: edge.targetHandle || 'input',
        }));
    }


    // ============================================================
    // Event Handlers
    // ============================================================

    /** Handle new connections between nodes. */
    const onConnect = useCallback(
        (params) => {
            const edge = {
                ...params,
                id: `edge_${params.source}_${params.target}`,
                animated: true,
                style: { stroke: '#6366f1', strokeWidth: 2 },
                markerEnd: { type: MarkerType.ArrowClosed, color: '#6366f1' },
            };
            setEdges((eds) => addEdge(edge, eds));
        },
        [setEdges]
    );

    /** Handle node selection — show config panel. */
    const onNodeClick = useCallback(
        (_event, node) => {
            setSelectedNode(node);
        },
        []
    );

    /** Handle clicks on the empty canvas — deselect node. */
    const onPaneClick = useCallback(() => {
        setSelectedNode(null);
    }, []);

    /**
     * Handle dropping a block from the sidebar onto the canvas.
     *
     * 1. Read the block type from the drag event's dataTransfer.
     * 2. Calculate the drop position in flow coordinates.
     * 3. Create a new node with default config.
     */
    const onDrop = useCallback(
        (event) => {
            event.preventDefault();

            const blockType = event.dataTransfer.getData('application/reactflow');
            if (!blockType || !BLOCK_TYPES[blockType]) return;

            // Convert screen coordinates to flow coordinates
            const position = reactFlowInstance.screenToFlowPosition({
                x: event.clientX,
                y: event.clientY,
            });

            const blockMeta = BLOCK_TYPES[blockType];
            const newNode = {
                id: generateId(),
                type: blockType,
                position,
                data: {
                    type: blockType,
                    label: blockMeta.label,
                    config: { ...blockMeta.defaultConfig },
                },
            };

            setNodes((nds) => [...nds, newNode]);
        },
        [reactFlowInstance, setNodes]
    );

    const onDragOver = useCallback((event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    /** Update a node's config from the config panel. */
    const onUpdateConfig = useCallback(
        (nodeId, newConfig, newLabel) => {
            setNodes((nds) =>
                nds.map((node) => {
                    if (node.id === nodeId) {
                        const updatedData = { ...node.data, config: newConfig };
                        if (newLabel !== undefined) {
                            updatedData.label = newLabel;
                        }
                        return { ...node, data: updatedData };
                    }
                    return node;
                })
            );
            // Also update selectedNode to keep panel in sync
            setSelectedNode((prev) => {
                if (prev && prev.id === nodeId) {
                    const updatedData = { ...prev.data, config: newConfig };
                    if (newLabel !== undefined) {
                        updatedData.label = newLabel;
                    }
                    return { ...prev, data: updatedData };
                }
                return prev;
            });
        },
        [setNodes]
    );

    /** Save the current canvas state. */
    const handleSave = () => {
        const blocks = nodesToBlocks(nodes);
        const connections = edgesToConnections(edges);
        onSave({ blocks, connections });
    };


    // ============================================================
    // Render
    // ============================================================

    return (
        <div className="workflow-editor">
            {/* Left: Block palette sidebar */}
            <Sidebar />

            {/* Center: React Flow canvas */}
            <div className="editor-canvas-wrapper" ref={reactFlowWrapper}>
                {/* Top toolbar */}
                <div className="editor-toolbar">
                    <div className="toolbar-left">
                        <h2 className="toolbar-title">
                            {workflow?.name || 'Untitled Workflow'}
                        </h2>
                        <span className={`badge badge-${workflow?.status || 'draft'}`}>
                            {workflow?.status || 'draft'}
                        </span>
                    </div>
                    <div className="toolbar-actions">
                        <button className="btn btn-secondary" onClick={() => onExport?.()}>
                            📄 Export Code
                        </button>
                        {workflow?.status === 'deployed' ? (
                            <button className="btn btn-danger" onClick={() => onUndeploy?.()}>
                                ⏸ Undeploy
                            </button>
                        ) : (
                            <button className="btn btn-success" onClick={() => onDeploy?.()}>
                                🚀 Deploy
                            </button>
                        )}
                        <button className="btn btn-primary" onClick={handleSave}>
                            💾 Save
                        </button>
                    </div>
                </div>

                {/* React Flow canvas */}
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onNodeClick={onNodeClick}
                    onPaneClick={onPaneClick}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    onInit={setReactFlowInstance}
                    nodeTypes={nodeTypes}
                    fitView
                    deleteKeyCode={['Backspace', 'Delete']}
                    className="editor-canvas"
                >
                    <Controls className="editor-controls" />
                    <MiniMap
                        className="editor-minimap"
                        nodeColor={(node) => {
                            const colors = {
                                input: '#3b82f6',
                                output: '#10b981',
                                db_query: '#f59e0b',
                                api_call: '#8b5cf6',
                                logic: '#ef4444',
                                transform: '#ec4899',
                            };
                            return colors[node.type] || '#6366f1';
                        }}
                        maskColor="rgba(0, 0, 0, 0.7)"
                        style={{ background: '#12121a' }}
                    />
                    <Background color="#2a2a3e" gap={20} size={1} />
                </ReactFlow>
            </div>

            {/* Right: Config panel (shown when a node is selected) */}
            {selectedNode && (
                <ConfigPanel
                    selectedNode={selectedNode}
                    onUpdateConfig={onUpdateConfig}
                    onClose={() => setSelectedNode(null)}
                />
            )}
        </div>
    );
}

export default WorkflowEditor;
