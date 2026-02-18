// ============================================================
// WorkflowEditor/Sidebar.jsx — Block Palette
// ============================================================
// The left sidebar of the editor that lists all available block
// types. Users drag blocks from here onto the canvas.
//
// Drag-and-drop is implemented using the HTML5 Drag API:
//   1. onDragStart stores the block type in dataTransfer.
//   2. The WorkflowEditor's onDrop handler reads it and creates
//      a new node at the drop position.
// ============================================================

import { BLOCK_TYPES } from './nodes/CustomNodes';
import './Sidebar.css';

// Order in which blocks appear in the sidebar
const BLOCK_ORDER = ['input', 'db_query', 'api_call', 'logic', 'transform', 'output'];


function Sidebar() {
    /**
     * Handle the start of dragging a block from the palette.
     * 
     * We store the block type in the drag event's dataTransfer
     * so the canvas drop handler knows what type of node to create.
     */
    const onDragStart = (event, blockType) => {
        event.dataTransfer.setData('application/reactflow', blockType);
        event.dataTransfer.effectAllowed = 'move';
    };

    return (
        <aside className="editor-sidebar">
            {/* Header */}
            <div className="sidebar-header">
                <h3 className="sidebar-title">
                    <span className="sidebar-icon">🧩</span>
                    Blocks
                </h3>
                <p className="sidebar-subtitle">Drag blocks to the canvas</p>
            </div>

            {/* Block list */}
            <div className="sidebar-blocks">
                {BLOCK_ORDER.map((blockType) => {
                    const block = BLOCK_TYPES[blockType];
                    return (
                        <div
                            key={blockType}
                            className="sidebar-block"
                            data-type={blockType}
                            draggable
                            onDragStart={(e) => onDragStart(e, blockType)}
                        >
                            <div className="sidebar-block-icon">{block.icon}</div>
                            <div className="sidebar-block-info">
                                <div className="sidebar-block-label">{block.label}</div>
                                <div className="sidebar-block-desc">{block.description}</div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Help tip */}
            <div className="sidebar-tip">
                <span className="tip-icon">💡</span>
                <span>Connect blocks by dragging from one handle to another</span>
            </div>
        </aside>
    );
}

export default Sidebar;
