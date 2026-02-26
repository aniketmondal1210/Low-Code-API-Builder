# 🚀 Low-Code API Builder Platform

> Build REST APIs visually — drag blocks, connect them, deploy with one click.
> [Try it out yourself, Now!! Visit LowCode Api Builder](https://low-code-api-builder.vercel.app/)

---

## 📖 Table of Contents

- [How It Works](#-how-it-works)
- [The 6 Block Types](#-the-6-block-types)
- [Under the Hood](#-under-the-hood)
- [Why It's Helpful](#-why-its-helpful)
- [Real-World Use Cases](#-real-world-use-cases)
- [Getting Started](#-getting-started)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)

---

## 🔧 How It Works

### The Core Idea

Instead of writing backend code manually, you **visually design** your API by connecting blocks on a canvas — like building with LEGO.

### Step-by-Step Flow

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. DESIGN  │ ──► │   2. SAVE    │ ──► │  3. DEPLOY   │ ──► │  4. USE IT   │
│  Drag blocks│     │  to MongoDB  │     │  One-click   │     │  Live API!   │
│  on canvas  │     │              │     │  endpoint    │     │  /api/gen/x  │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

1. **Design** — Open the visual editor, drag blocks from the sidebar onto the canvas
2. **Connect** — Draw lines between blocks to define the data flow
3. **Configure** — Click any block to set its parameters (collection name, query, fields, etc.)
4. **Save** — Your workflow is stored as JSON in MongoDB
5. **Deploy** — One click creates a live API endpoint at `/api/generated/<your-workflow-name>`
6. **Use** — Call your new API from anywhere — Postman, curl, frontend apps, other services

---

## 🧱 The 6 Block Types

| Block | Color | What It Does | Example Config |
|-------|-------|-------------|----------------|
| 🟦 **Input** | Blue | Defines what data the API accepts | `{ "name": string, "age": number }` |
| 🟩 **Database Query** | Green | Reads/writes to MongoDB collections | Find all users where `age > 25` |
| 🟪 **API Call** | Purple | Calls external APIs (HTTP requests) | Fetch weather from OpenWeatherMap |
| 🟨 **Logic** | Yellow | If-else conditional branching | If `age >= 18` → "adult", else → "minor" |
| 🟧 **Transform** | Orange | Reshapes, renames, or filters data | Rename `first_name` → `name`, compute totals |
| 🟢 **Output** | Teal | Formats the final API response | Return `{ "status": "success", "data": [...] }` |

### Block Details

#### 🟦 Input Block
Defines the expected request body schema. Validates incoming data automatically.

```json
{
  "fields": [
    { "name": "username", "type": "string", "required": true },
    { "name": "age", "type": "number", "required": false }
  ]
}
```

#### 🟩 Database Query Block
Performs MongoDB operations with template interpolation.

```json
{
  "collection": "users",
  "operation": "find",
  "query": { "age": { "$gt": "{{request_data.age}}" } },
  "limit": 50
}
```

**Supported operations:** `find`, `insert`, `update`, `delete`

#### 🟪 API Call Block
Makes HTTP requests to external services.

```json
{
  "url": "https://api.example.com/data",
  "method": "GET",
  "headers": { "Authorization": "Bearer {{request_data.token}}" }
}
```

**Supported methods:** `GET`, `POST`, `PUT`, `DELETE`

#### 🟨 Logic Block
Evaluates conditions and routes data flow accordingly.

```json
{
  "condition": "request_data.age >= 18",
  "true_value": { "category": "adult" },
  "false_value": { "category": "minor" }
}
```

Uses a **safe evaluator** — no `eval()`, no code injection risks.

#### 🟧 Transform Block
Manipulates data between blocks.

```json
{
  "operation": "map_fields",
  "mapping": {
    "full_name": "{{request_data.first_name}} {{request_data.last_name}}",
    "is_adult": "{{logic_1.category}}"
  }
}
```

**Supported operations:** `map_fields`, `rename_fields`, `filter_array`, `pick_fields`, `merge`

#### 🟢 Output Block
Defines the final HTTP response.

```json
{
  "status_code": 200,
  "body": {
    "message": "Success",
    "data": "{{db_query_1.results}}",
    "count": "{{db_query_1.count}}"
  }
}
```

---

## ⚙️ Under the Hood

### What Happens When You Deploy

```
User clicks "Deploy"
        │
        ▼
Workflow JSON saved to MongoDB with status: "deployed"
        │
        ▼
Dynamic route /api/generated/<name> is now active
        │
        ▼
When someone calls the endpoint:
        │
        ├── 1. Request hits Flask catch-all route
        ├── 2. Looks up workflow by name in MongoDB
        ├── 3. Workflow Engine parses the JSON
        ├── 4. Topological Sort determines execution order
        ├── 5. Executes blocks one by one:
        │       Input → DB Query → Transform → Logic → Output
        ├── 6. Each block's output is stored in shared context
        ├── 7. Template interpolation fills in {{variables}}
        └── 8. Final Output block returns HTTP response
```

### Template Interpolation

The `{{variable}}` syntax lets blocks reference each other's outputs:

```
{{request_data.name}}       → Value from the API request body
{{db_query_1.results}}      → Results from a database query block
{{api_call_1.response}}     → Response from an external API call
{{logic_1.result}}          → Result from a logic block
{{transform_1.data}}        → Output from a transform block
```

### Execution Engine

The workflow engine uses **topological sorting** to determine the correct execution order:

```
Example: Input → [DB Query, API Call] → Transform → Output

Topological sort ensures:
  1. Input runs first (no dependencies)
  2. DB Query and API Call run next (depend on Input)
  3. Transform runs after both complete (depends on their outputs)
  4. Output runs last (depends on Transform)
```

This means blocks can have **parallel dependencies** — the engine figures out the right order automatically.

---

## 💡 Why It's Helpful

### 1. ⚡ Speed — Build APIs in Minutes, Not Hours

| Approach | Time to Build a CRUD API |
|----------|--------------------------|
| Traditional coding (Flask/Express) | 2-4 hours |
| With this tool | 5-10 minutes |

### 2. 🎯 No Backend Expertise Needed

- Frontend developers can create APIs without learning Flask/Django/Express
- Data analysts can expose their queries as endpoints
- Product managers can prototype backends for demos

### 3. 👁️ Visual Understanding

- **See** the data flow instead of reading code
- Easy to debug — just follow the arrows on the canvas
- New team members understand the API logic instantly

### 4. 🚀 Instant Deployment

- One click → live API endpoint
- No server configuration needed
- No deployment pipeline to set up
- Endpoint is immediately callable

### 5. 📋 Auto-Generated Documentation

- Swagger/OpenAPI docs are created automatically from your workflow
- Interactive — anyone can test your API from the docs page
- Always up-to-date with your workflow design

### 6. 📤 Code Export

- Need the actual Python code? Click "Export Code"
- Get a standalone Flask file you can run anywhere
- Great for learning how backend code works
- Useful for migrating away from the visual tool when you outgrow it

---

## 🌍 Real-World Use Cases

| Scenario | How This Tool Helps |
|----------|-------------------|
| **Hackathons** | Build a full backend in 30 minutes, focus on the idea |
| **MVP/Prototypes** | Test your startup idea without hiring a backend developer |
| **Internal Tools** | Quick CRUD APIs for your team's MongoDB data |
| **Teaching** | Show students how APIs work with a visual interface |
| **Microservices** | Spin up simple endpoints without writing boilerplate |
| **Data Pipelines** | Chain API calls and DB queries visually |
| **Webhook Handlers** | Accept webhooks and process them through visual logic |

### Example: Building a "Get Users by Age" API

**Traditional approach (Flask):**
```python
@app.route('/api/users', methods=['POST'])
def get_users():
    data = request.get_json()
    age = data.get('age', 0)
    if not isinstance(age, int):
        return jsonify({'error': 'age must be a number'}), 400
    users = list(db.users.find({'age': {'$gt': age}}))
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify({'users': users, 'count': len(users)})
```

**With this tool:**
1. Drag an **Input** block → add field `age` (number)
2. Drag a **Database** block → collection `users`, operation `find`, query `{age: {$gt: {{request_data.age}}}}`
3. Drag an **Output** block → body `{users: {{db_query_1.results}}}`
4. Connect: Input → Database → Output
5. Click Deploy ✅

**Same result, zero code written!**

---

## 🏁 Getting Started

### Prerequisites

- **Python 3.8+** installed
- **Node.js 16+** installed
- **MongoDB** running (local or [MongoDB Atlas](https://www.mongodb.com/cloud/atlas))

### Installation

```bash
# 1. Clone the project
cd "low-code-api-builder"

# 2. Set up Python backend
pip install -r requirements.txt

# 3. Set up React frontend
cd frontend
npm install
cd ..

# 4. Configure environment
# Edit .env file with your MongoDB connection string
```

### Running the Application

```bash
# Terminal 1 — Start Backend
cd "c:\Users\anike\Downloads\AniketCodes\PEP Project"
python backend/app.py

# Terminal 2 — Start Frontend
cd "c:\Users\anike\Downloads\AniketCodes\PEP Project\frontend"
npm run dev
```

### URLs

| Service | URL |
|---------|-----|
| **Frontend (Dashboard)** | http://localhost:5173 |
| **Backend API** | http://localhost:5000 |
| **Swagger Docs** | http://localhost:5000/swagger/ |
| **Generated Endpoints** | http://localhost:5000/api/generated/<name> |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────┐
│                   FRONTEND                     │
│              (React + Vite)                    │
│                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Dashboard │  │  Editor  │  │   Docs   │      │
│  │  Page    │  │   Page   │  │   Page   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                     │                          │
│              ┌──────┴──────┐                   │
│              │  React Flow │                   │
│              │   Canvas    │                   │
│              └─────────────┘                   │
│                     │                          │
│              ┌──────┴──────┐                   │
│              │  API Client │ (Axos)            │
│              └──────┬──────┘                   │
└─────────────────────┼──────────────────────────┘
                      │ HTTP
┌─────────────────────┼──────────────────────────┐
│                BACKEND (Flask)                 │
│                    │                           │
│  ┌─────────────────┴──────────────────────┐    │
│  │            Route Blueprints            │    │
│  │                                        │    │
│  │  /api/workflows    → CRUD operations   │    │
│  │  /api/generated/*  → Dynamic endpoints │    │
│  │  /api/docs/*       → Swagger specs     │    │
│  └─────────────┬──────────────────────────┘    │
│                │                               │
│  ┌─────────────┴──────────────────────────┐    │
│  │         Workflow Enge                  │    │
│  │  ┌───────┐ ┌────────┐ ┌──────────┐     │    │
│  │  │Input  │ │DB Query│ │API Call  │     │    │
│  │  │Handler│ │Handler │ │Handler   │     │    │
│  │  └───────┘ └────────┘ └──────────┘     │    │
│  │  ┌───────┐ ┌─────────┐ ┌─────────┐     │    │
│  │  │Logic  │ │Transform│ │Output   │     │    │
│  │  │Handler│ │Handler  │ │Handler  │     │    │
│  │  └───────┘ └─────────┘ └─────────┘     │    │
│  └────────────────────────────────────────┘    │
│                │                               │
│  ┌─────────────┴───────────┐                   │
│  │    Code Generator       │                   │
│  │  • Flask code export    │                   │
│  │  • OpenAPI spec gen     │                   │
│  └─────────────────────────┘                   │
└────────────────────┼────────────────────────── ┘
                     │
┌────────────────────┼───────────────────────────┐
│              MongoDB Database                  │
│                    │                           │
│  ┌─────────────────┴──────────────────────┐    │
│  │  workflows collection                  │    │
│  │  ┌──────────────────────────────────┐  │    │
│  │  │ { name, blocks, connections,     │  │    │
│  │  │   status, created_at, updated_at}│  │    │
│  │  └──────────────────────────────────┘  │    │
│  └────────────────────────────────────────┘    │
└────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 19 | UI components |
| **Canvas** | React Flow | Drag-and-drop node editor |
| **Bundler** | Vite 7 | Fast dev server & build |
| **HTTP Client** | Axios | Frontend → Backend API calls |
| **API Docs** | Swagger UI React | Interactive API documentation |
| **Backend** | Flask (Python) | REST API server |
| **Database** | MongoDB (Atlas) | Workflow storage |
| **DB Driver** | PyMongo | Python ↔ MongoDB |
| **CORS** | Flask-CORS | Cross-origin request handling |

---

## 📁 Project Structure

```
PEP Project/
├── backend/
│   ├── app.py                  # Flask application factory
│   ├── config.py               # Environment configuration
│   ├── extensions.py           # MongoDB connection manager
│   ├── workflow_engine.py      # Core execution engine (600+ lines)
│   ├── code_generator.py       # Flask code & OpenAPI export
│   ├── models/
│   │   └── workflow.py         # Workflow CRUD operations
│   └── routes/
│       ├── workflow_routes.py  # REST API for workflow management
│       ├── generated_routes.py # Dynamic endpoint dispatcher
│       └── docs_routes.py      # Swagger/OpenAPI endpoints
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # React Router setup
│   │   ├── index.css           # Dark mode design system
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx   # Workflow list & management
│   │   │   ├── EditorPage.jsx  # Editor container
│   │   │   └── DocsPage.jsx    # Swagger viewer
│   │   ├── components/
│   │   │   └── WorkflowEditor/
│   │   │       ├── WorkflowEditor.jsx  # React Flow canvas
│   │   │       ├── ConfigPanel.jsx     # Block configuration forms
│   │   │       ├── Sidebar.jsx         # Draggable block palette
│   │   │       └── nodes/
│   │   │           └── CustomNodes.jsx # 6 custom node components
│   │   └── services/
│   │       └── api.js          # Axios API client
│   └── package.json            # Frontend dependencies
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── HOW_IT_WORKS.md             # ← You are here!
```

---

## 🔐 Security Features

- **No `eval()`** — Logic blocks use safe string parsing, preventing code injection
- **CORS configured** — Only allowed frontend origins can make requests
- **Schema validation** — Input blocks enforce type checking on incoming data
- **Parameterized queries** — MongoDB operations use PyMongo's safe query builder
- **Graceful degradation** — Server starts even if MongoDB is temporarily unavailable

---

## 📝 API Reference

### Workflow Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/workflows` | List all workflows |
| `POST` | `/api/workflows` | Create a new workflow |
| `GET` | `/api/workflows/:id` | Get a specific workflow |
| `PUT` | `/api/workflows/:id` | Update a workflow |
| `DELETE` | `/api/workflows/:id` | Delete a workflow |
| `POST` | `/api/workflows/:id/deploy` | Deploy (activate endpoint) |
| `POST` | `/api/workflows/:id/undeploy` | Undeploy (deactivate endpoint) |
| `GET` | `/api/workflows/:id/export` | Export as standalone Flask code |

### Generated Endpoints

|        Method         |        Endpoint         |         Description         |
|-----------------------|-------------------------|-----------------------------|
| `GET/POST/PUT/DELETE` | `/api/generated/:name`  | Execute a deployed workflow |

### Documentation

| Method  |         Endpoint         |         Description       |
|---------|--------------------------|---------------------------|
|  `GET`  | `/api/docs/openapi.json` | OpenAPI 3.0 specification |
|  `GET`  | `/swagger/`              | Interactive Swagger UI    |

---

*Built with ❤️ — making API development accessible to everyone.*
