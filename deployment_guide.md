# 🚀 Deployment Guide — Low-Code API Builder Platform

> **Frontend** → Vercel (React + Vite)  
> **Backend** → Render (Flask + Gunicorn)  
> **Database** → MongoDB Atlas (cloud-hosted)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Architecture Overview](#2-architecture-overview)
3. [Step 1 — Database (MongoDB Atlas)](#3-step-1--database-mongodb-atlas)
4. [Step 2 — Backend on Render](#4-step-2--backend-on-render)
5. [Step 3 — Frontend on Vercel](#5-step-3--frontend-on-vercel)
6. [Step 4 — Connect Frontend ↔ Backend](#6-step-4--connect-frontend--backend)
7. [Environment Variables Reference](#7-environment-variables-reference)
8. [Project Structure (Deployment Files)](#8-project-structure-deployment-files)
9. [Troubleshooting](#9-troubleshooting)
10. [Updating After Deployment](#10-updating-after-deployment)

---

## 1. Prerequisites

Before deploying, make sure you have:

- [x] A **GitHub** repository with your project pushed
- [x] A **MongoDB Atlas** account — [Sign up free](https://www.mongodb.com/cloud/atlas/register)
- [x] A **Render** account — [Sign up free](https://render.com/)
- [x] A **Vercel** account — [Sign up free](https://vercel.com/signup)
- [x] Your project builds locally without errors

---

## 2. Architecture Overview

```
┌─────────────────────┐         ┌─────────────────────┐
│                     │  HTTPS  │                     │
│   Vercel (Frontend) │ ◄─────► │  Render (Backend)   │
│   React + Vite      │  API    │  Flask + Gunicorn   │
│                     │  calls  │                     │
└─────────────────────┘         └──────────┬──────────┘
                                           │
                                           │ MongoDB Driver
                                           ▼
                                ┌─────────────────────┐
                                │  MongoDB Atlas      │
                                │  (Cloud Database)   │
                                └─────────────────────┘
```

**How it works:**
- The **frontend** (React app) is built into static files and served by Vercel's CDN.
- The **backend** (Flask API) runs on Render as a web service with Gunicorn (production WSGI server).
- Both connect to **MongoDB Atlas** for data persistence.
- The frontend communicates with the backend via the `VITE_API_URL` environment variable.
- The backend allows the frontend via the `FRONTEND_URL` environment variable (CORS).

---

## 3. Step 1 — Database (MongoDB Atlas)

> ⚠️ **If you already have a MongoDB Atlas cluster, skip to Step 2.**

### 3.1 Create a Free Cluster

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/) and sign in.
2. Click **"Build a Cluster"** → Choose the **Free Tier (M0)**.
3. Select a cloud provider and region close to your Render region.
4. Click **"Create Cluster"** and wait for provisioning (~2 minutes).

### 3.2 Configure Access

1. **Database Access** → Click "Add New Database User":
   - Username: `your_db_user`
   - Password: Generate a secure password (save it!)
   - Role: "Read and write to any database"

2. **Network Access** → Click "Add IP Address":
   - Click **"Allow Access From Anywhere"** (`0.0.0.0/0`)
   - This is required for Render's dynamic IP addresses.

### 3.3 Get Your Connection String

1. Click **"Connect"** on your cluster.
2. Choose **"Connect your application"**.
3. Copy the connection string. It will look like:

```
mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/api_builder?retryWrites=true&w=majority
```

4. Replace `<username>` and `<password>` with your database user credentials.
5. Make sure the database name (after the `/`) is `api_builder`.
6. **Save this string** — you'll need it for the backend deployment.

---

## 4. Step 2 — Backend on Render

### 4.1 Create a New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/).
2. Click **"New +"** → **"Web Service"**.
3. Connect your **GitHub repository**.
4. Configure the service:

| Setting | Value |
|---|---|
| **Name** | `low-code-api-builder-backend` |
| **Region** | Choose closest to your MongoDB Atlas cluster |
| **Branch** | `main` (or your default branch) |
| **Root Directory** | *(leave blank — project root)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120` |
| **Plan** | Free |

> 💡 **Tip:** The Start Command is also in the `Procfile`, so Render may auto-detect it. But it's good to set it explicitly.

### 4.2 Set Environment Variables

In the Render dashboard, go to your service → **"Environment"** tab → Add these variables:

| Key | Value | Notes |
|---|---|---|
| `MONGO_URI` | `mongodb+srv://user:pass@cluster0.xxx.net/api_builder?...` | Your Atlas connection string |
| `FLASK_SECRET_KEY` | *(generate a random string)* | Use: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_DEBUG` | `False` | **Must be False in production!** |
| `FLASK_PORT` | `5000` | Port for Flask (Render maps it internally) |
| `FRONTEND_URL` | *(set after frontend deploy)* | e.g., `https://your-app.vercel.app` |
| `PYTHON_VERSION` | `3.11.11` | Specify Python version for Render |

### 4.3 Deploy

1. Click **"Create Web Service"**.
2. Render will install dependencies and start the server.
3. Wait for the deploy to complete (~2-5 minutes).
4. Your backend will be live at: `https://your-service-name.onrender.com`

### 4.4 Verify

Test the health check endpoint:

```bash
curl https://your-service-name.onrender.com/
```

Expected response:
```json
{
  "status": "running",
  "service": "Low-Code API Builder Platform",
  "version": "1.0.0",
  "endpoints": { ... }
}
```

> 📝 **Note:** Free Render services spin down after 15 minutes of inactivity. The first request after inactivity may take ~30-50 seconds.

---

## 5. Step 3 — Frontend on Vercel

### 5.1 Import Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **"Add New ..."** → **"Project"**.
3. **Import** your GitHub repository.
4. Configure the project:

| Setting | Value |
|---|---|
| **Framework Preset** | `Vite` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` *(auto-detected)* |
| **Output Directory** | `dist` *(auto-detected)* |
| **Install Command** | `npm install` *(auto-detected)* |

### 5.2 Set Environment Variables

Before clicking "Deploy", add the environment variable:

| Key | Value | Environment |
|---|---|---|
| `VITE_API_URL` | `https://your-service-name.onrender.com/api` | Production |

> ⚠️ **Important:** The `VITE_` prefix is required! Vite only exposes env vars with this prefix to the browser bundle.

> ⚠️ **No trailing slash** on the URL! Correct: `.../api` — Wrong: `.../api/`

### 5.3 Deploy

1. Click **"Deploy"**.
2. Vercel will install dependencies, build the React app, and deploy it.
3. Your frontend will be live at: `https://your-project.vercel.app`

### 5.4 Verify

1. Open your Vercel URL in the browser.
2. You should see the Dashboard page.
3. Try creating a workflow to verify the backend connection works.

---

## 6. Step 4 — Connect Frontend ↔ Backend

After both services are deployed, you need to set the CORS origin on the backend:

### 6.1 Update Backend CORS

1. Go to **Render Dashboard** → Your backend service → **Environment**.
2. Set the `FRONTEND_URL` variable to your Vercel URL:
   ```
   FRONTEND_URL=https://your-project.vercel.app
   ```
3. Click **"Save Changes"** — Render will automatically redeploy.

### 6.2 Verify the Connection

1. Open your Vercel app in the browser.
2. Open **DevTools → Console** (F12).
3. Try creating a workflow.
4. Check that there are **no CORS errors** in the console.

If you see CORS errors, double-check:
- The `FRONTEND_URL` on Render matches your Vercel URL **exactly** (no trailing slash).
- The backend has redeployed after the env var change.

---

## 7. Environment Variables Reference

### Backend (Render)

| Variable | Required | Default | Description |
|---|---|---|---|
| `MONGO_URI` | ✅ Yes | `mongodb://localhost:27017/api_builder` | MongoDB Atlas connection string |
| `FLASK_SECRET_KEY` | ✅ Yes | `dev-secret-key` | Secret key for Flask sessions |
| `FLASK_DEBUG` | ❌ No | `True` | **Set to `False` in production** |
| `FLASK_PORT` | ❌ No | `5000` | Flask server port |
| `FRONTEND_URL` | ✅ Yes | *(empty)* | Vercel frontend URL for CORS |
| `PYTHON_VERSION` | ❌ No | — | Python version for Render |

### Frontend (Vercel)

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | ✅ Yes | `http://localhost:5000/api` | Backend API URL on Render |

---

## 8. Project Structure (Deployment Files)

These are the files involved in deployment:

```
PEP Project/
├── Procfile                     # Render: gunicorn start command
├── render.yaml                  # Render Blueprint (Infrastructure as Code)
├── runtime.txt                  # Python version for Render
├── requirements.txt             # Python deps (includes gunicorn)
├── .env                         # Local dev env vars (gitignored)
├── .env.example                 # Template for env vars
│
├── backend/
│   ├── app.py                   # Flask app factory + dynamic CORS
│   ├── config.py                # Centralized config (reads env vars)
│   ├── extensions.py            # MongoDB connection (robust URI parsing)
│   ├── code_generator.py        # Generates Flask code for workflows
│   ├── workflow_engine.py       # Executes workflows at runtime
│   ├── models/
│   │   └── workflow.py          # MongoDB model for workflows
│   └── routes/
│       ├── workflow_routes.py   # CRUD API for workflows
│       ├── generated_routes.py  # Dynamic endpoint execution
│       └── docs_routes.py       # OpenAPI spec (dynamic server URL)
│
└── frontend/
    ├── vercel.json              # Vercel: SPA routing + caching
    ├── .env.example             # Template for VITE_API_URL
    ├── index.html               # Entry point (SEO meta tags)
    └── src/
        ├── services/api.js      # Axios client (uses VITE_API_URL)
        └── pages/DocsPage.jsx   # Swagger UI (uses VITE_API_URL)
```

---

## 9. Troubleshooting

### ❌ CORS Errors in Browser Console

```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Fix:** Ensure `FRONTEND_URL` is set correctly on Render:
- Must include `https://` prefix
- Must NOT have a trailing slash
- Example: `https://your-app.vercel.app`

After changing, wait for Render to redeploy (~1-2 min).

---

### ❌ Backend Returns 503 (Database Unavailable)

```json
{ "error": "Database Unavailable" }
```

**Fix:**
1. Check `MONGO_URI` is correct on Render dashboard.
2. Ensure MongoDB Atlas **Network Access** allows `0.0.0.0/0`.
3. If password contains special chars (`@`, `#`, etc.), URL-encode them.
4. Verify the database name in the URI is `api_builder` (after the last `/`, before `?`).

---

### ❌ Frontend Shows Blank Page / 404 on Refresh

**Fix:** Ensure `vercel.json` exists in the `frontend/` directory with the SPA rewrite rule:
```json
{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
```

---

### ❌ Render Build Fails with ModuleNotFoundError

```
ModuleNotFoundError: No module named 'gunicorn'
```

**Fix:** Ensure `gunicorn==23.0.0` is in `requirements.txt` and the **Build Command** is `pip install -r requirements.txt`.

---

### ❌ Render Gunicorn Start Command Fails

```
Error: No module named 'backend'
```

**Fix:** Make sure the **Root Directory** on Render is **blank** (project root), NOT `backend/`. Gunicorn needs to run from the project root so `wsgi.py` and the `backend` package are importable.

> 💡 We use a `wsgi.py` entry point file instead of `backend.app:create_app()` because Render's bash shell interprets the parentheses `()` as shell syntax and throws an error.

---

### ❌ API Calls Failing on Vercel (Wrong URL)

**Fix:**
1. Check `VITE_API_URL` is set in Vercel → Settings → Environment Variables.
2. Ensure it points to `https://your-backend.onrender.com/api` (with `/api` at the end).
3. **Redeploy** the frontend after changing env vars (Vite embeds them at build time!).

---

### ❌ Swagger Docs Page Shows Wrong Server URL

The OpenAPI spec dynamically detects the server URL from the incoming request. If it shows `localhost`, make sure you're accessing the Swagger docs through the deployed URL, not localhost.

---

### ❌ Render Free Tier Cold Starts (Slow First Request)

The free tier spins down after 15 minutes of inactivity. First request takes ~30-50 seconds.

**Workaround options:**
1. Use a free uptime monitor (e.g., [UptimeRobot](https://uptimerobot.com/)) to ping `/` every 14 minutes.
2. Upgrade to Render's paid plan for always-on instances.

---

## 10. Updating After Deployment

### Automatic Deploys

Both Vercel and Render support **auto-deploy on push**:
- Push to your `main` branch → both services redeploy automatically.

### Manual Redeploy

- **Render:** Dashboard → Your service → "Manual Deploy" → "Deploy latest commit"
- **Vercel:** Dashboard → Your project → "Deployments" → "Redeploy"

### Changing Environment Variables

- **Backend (Render):** Change env vars → service auto-redeploys.
- **Frontend (Vercel):** Change env vars → you **must manually redeploy** (Vite embeds env vars at build time).

---

## ✅ Deployment Checklist

Use this checklist to verify everything is set up correctly:

- [ ] MongoDB Atlas cluster is created and accessible
- [ ] Atlas Network Access allows `0.0.0.0/0`
- [ ] Backend deployed on Render with all env vars set
- [ ] Render **Root Directory** is blank (not `backend/`)
- [ ] Backend health check (`/`) returns `200 OK`
- [ ] Frontend deployed on Vercel with `VITE_API_URL` set
- [ ] Vercel **Root Directory** is set to `frontend`
- [ ] `FRONTEND_URL` on Render points to Vercel URL
- [ ] Frontend loads correctly in browser
- [ ] Creating/editing workflows works (frontend ↔ backend)
- [ ] Swagger docs page loads at `/docs`
- [ ] No CORS errors in browser console

---

**🎉 Congratulations! Your Low-Code API Builder Platform is now live!**
