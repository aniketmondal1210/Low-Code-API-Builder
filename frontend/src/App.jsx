// ============================================================
// App.jsx — Root Application Component
// ============================================================
// Sets up client-side routing with React Router.
//
// Routes:
//   /            → Dashboard (workflow list)
//   /editor/:id  → Visual workflow editor
//   /docs        → Swagger API documentation
// ============================================================

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import EditorPage from './pages/EditorPage';
import DocsPage from './pages/DocsPage';


function App() {
  return (
    <Router>
      <Routes>
        {/* Dashboard — list all workflows */}
        <Route path="/" element={<Dashboard />} />

        {/* Editor — visual workflow builder */}
        <Route path="/editor/:id" element={<EditorPage />} />

        {/* Docs — Swagger UI for generated APIs */}
        <Route path="/docs" element={<DocsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
