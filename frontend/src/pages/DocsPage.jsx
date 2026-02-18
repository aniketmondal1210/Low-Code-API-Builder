// ============================================================
// pages/DocsPage.jsx — Embedded Swagger Documentation
// ============================================================
// Renders the auto-generated OpenAPI docs using Swagger UI React.
// The docs are fetched from the backend's /api/docs/openapi.json
// endpoint, which dynamically builds the spec from all deployed
// workflows.
// ============================================================

import { useNavigate } from 'react-router-dom';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
import './DocsPage.css';


function DocsPage() {
    const navigate = useNavigate();

    return (
        <div className="docs-page">
            {/* Navigation */}
            <nav className="docs-nav">
                <button className="btn btn-ghost" onClick={() => navigate('/')}>
                    ← Dashboard
                </button>
                <h2 className="docs-nav-title">📚 API Documentation</h2>
                <div style={{ width: 100 }} /> {/* Spacer for centering */}
            </nav>

            {/* Swagger UI */}
            <div className="docs-content">
                <SwaggerUI
                    url="http://localhost:5000/api/docs/openapi.json"
                    docExpansion="list"
                    defaultModelsExpandDepth={-1}
                    filter={true}
                />
            </div>
        </div>
    );
}

export default DocsPage;
