# Production Deployment Plan: Vercel (Frontend) & Railway (Backend)
## AI-Powered Discovery Engine for Google Photos Retrieval

> **Document Version:** 1.0.0  
> **Status:** Production-Ready  
> **Target Platforms:** **Vercel** (Frontend SPA) & **Railway** (FastAPI Backend + Database)  
> **Governing Documents:**  
> - [Problem statement.md](file:///c:/Users/ADMIN/Desktop/PRODUCT%20OWNER%20PROJECT%203/AI%20Discovery%20Engine/Problem%20statement.md)  
> - [Architecture.md](file:///c:/Users/ADMIN/Desktop/PRODUCT%20OWNER%20PROJECT%203/AI%20Discovery%20Engine/Architecture.md)  
> - [Implementation plan.md](file:///c:/Users/ADMIN/Desktop/PRODUCT%20OWNER%20PROJECT%203/AI%20Discovery%20Engine/Implementation%20plan.md)

---

## 1. Architectural Overview & Network Topology

The **AI-Powered Discovery Engine** uses a decoupled, cloud-native architecture optimized for zero-maintenance hosting, high-throughput static caching, and dedicated Python ML/analytics compute:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          USER BROWSER / CLIENT                         │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
              HTTPS Requests       │
         ┌─────────────────────────┴────────────────────────┐
         │                                                  │
         ▼ (Page Loads & Static Assets)                     ▼ (API Calls / Cues)
┌──────────────────────────────────┐               ┌──────────────────────────────────┐
│         VERCEL EDGE CDN          │               │        VERCEL REVERSE PROXY      │
│  React 18 + Vite SPA             │               │  Route rewrites:                 │
│  - Recharts Visualizations       │               │  - /api/:path* -> Railway        │
│  - Evidence Explorer             │               │  - /health     -> Railway        │
│  - AI Research Copilot UI        │               │  (Zero CORS friction)            │
└──────────────────────────────────┘               └─────────────────┬────────────────┘
                                                                     │
                                                    Encrypted HTTPS  │
                                                                     ▼
                                                   ┌──────────────────────────────────┐
                                                   │        RAILWAY CONTAINER         │
                                                   │  Python 3.12 / FastAPI (Uvicorn) │
                                                   │  - /health & /api/v1/overview    │
                                                   │  - /api/v1/clusters & /ask       │
                                                   │  - 7-Dimension LLM Pipeline      │
                                                   │  - SQLite (discovery_engine.db)  │
                                                   │    or Railway PostgreSQL         │
                                                   └─────────────────┬────────────────┘
                                                                     │
                                                    Inference API    │
                                                                     ▼
                                                   ┌──────────────────────────────────┐
                                                   │         GROQ CLOUD LPUs          │
                                                   │  - openai/gpt-oss-120b           │
                                                   │  - openai/gpt-oss-20b            │
                                                   │  - qwen/qwen3.8-27b              │
                                                   └──────────────────────────────────┘
```

### Why This Split Deployment Architecture?
1. **Zero CORS Friction:** Vercel reverse-proxies `/api/*` and `/health` requests directly to Railway. The frontend can make relative requests (`/api/v1/overview`) without cross-origin blocks or strict browser security barriers.
2. **Sub-50ms Global Edge Delivery:** The React SPA bundle is served statically across Vercel's global edge network with instant cache-invalidation.
3. **Dedicated Python & ML Execution:** Machine learning dependencies (`scikit-learn`, `numpy`, `pandas`, `sqlalchemy`, `instructor`, `groq`) run inside an isolated Linux container on Railway with dedicated compute and memory.
4. **Persistent Qualitative Evidence:** The SQLite metadata store (`discovery_engine.db`) and vector index persist on Railway storage, with immediate upgrade compatibility to Railway PostgreSQL.

---

## 2. Pre-Deployment Repository Preparation

### 2.1 Repository Directory Structure
Ensure the repository contains the decoupled root structure:

```
AI Discovery Engine/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints.py
│   │   ├── core/config.py
│   │   ├── core/database.py
│   │   ├── models/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.ts
│   │   ├── data/mockDiscoveryData.ts
│   │   └── App.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── vercel.json           <-- Vercel deployment config
├── docs/
│   └── deployment-plan.md     <-- This file
├── discovery_engine.db        <-- SQLite database with harvested evidence
├── docker-compose.yml
└── .env.example
```

---

### 2.2 Backend Requirements Check
Verify [`backend/requirements.txt`](file:///c:/Users/ADMIN/Desktop/PRODUCT%20OWNER%20PROJECT%203/AI%20Discovery%20Engine/backend/requirements.txt) contains all required production dependencies:

```txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
pydantic-settings>=2.2.0
groq>=0.5.0
instructor>=1.2.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
google-play-scraper>=1.2.4
praw>=7.7.1
sentence-transformers>=2.5.0
scikit-learn>=1.4.0
pandas>=2.2.0
numpy>=1.26.0
requests>=2.31.0
httpx>=0.27.0
pytest>=8.0.0
```

---

### 2.3 Backend Railway Configuration (`Procfile` / `railway.json`)
To enable Railway to detect and run the FastAPI service effortlessly, add a [`Procfile`](file:///c:/Users/ADMIN/Desktop/PRODUCT%20OWNER%20PROJECT%203/AI%20Discovery%20Engine/Procfile) in the repository root:

```procfile
web: uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Or configure Railway to build with the existing [`backend/Dockerfile`](file:///c:/Users/ADMIN/Desktop/PRODUCT%20OWNER%20PROJECT%203/AI%20Discovery%20Engine/backend/Dockerfile):
```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

---

### 2.4 Frontend Vercel Configuration (`frontend/vercel.json`)
Create [`frontend/vercel.json`](file:///c:/Users/ADMIN/Desktop/PRODUCT%20OWNER%20PROJECT%203/AI%20Discovery%20Engine/frontend/vercel.json) to establish reverse-proxying and SPA client-side routing:

```json
{
  "version": 2,
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR-RAILWAY-BACKEND-URL.up.railway.app/api/:path*"
    },
    {
      "source": "/health",
      "destination": "https://YOUR-RAILWAY-BACKEND-URL.up.railway.app/health"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## 3. Phase 1: Deploying Backend to Railway

### Step 1.1: Push Project to GitHub
Initialize a git repository if not already tracked and push to GitHub:
```powershell
git init
git add .
git commit -m "feat: complete AI Discovery Engine ready for production deployment"
git branch -M main
git remote add origin https://github.com/<your-username>/ai-discovery-engine.git
git push -u origin main
```

---

### Step 1.2: Create New Project on Railway
1. Log into your **Railway Dashboard** at [railway.com](https://railway.com/).
2. Click **`+ New Project`** &rarr; **`Deploy from GitHub repo`**.
3. Select your repository: `ai-discovery-engine`.

---

### Step 1.3: Configure Railway Service Settings
1. Click on the newly created service tile &rarr; go to the **Settings** tab.
2. **Build Configuration**:
   - **Builder**: `Nixpacks` (Default) OR `Dockerfile`.
   - If using `Dockerfile`: set Dockerfile Path to `backend/Dockerfile`.
   - If using `Nixpacks`: set **Start Command** to:
     ```bash
     uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
     ```
3. **Networking**:
   - Under **Networking**, click **`Generate Domain`**.
   - Railway will provide a public URL such as:
     `https://ai-discovery-engine-production.up.railway.app`
   - Copy this URL (needed for Vercel configuration in Phase 2).

---

### Step 1.4: Add Railway Environment Variables
Navigate to the **Variables** tab in Railway and add the following keys:

| Variable Name | Recommended Value | Purpose |
| :--- | :--- | :--- |
| `APP_ENV` | `production` | Enables production optimizations & logs |
| `LOG_LEVEL` | `info` | Structured logging level |
| `SECRET_KEY` | *(generate a 32+ char random key)* | Security token & signing |
| `GROQ_API_KEY` | `gsk_...` | Groq LPU API Key for real-time LLM synthesis |
| `GROQ_MODEL_EXTRACTION` | `openai/gpt-oss-120b` | High-fidelity 7-dimension extraction |
| `GROQ_MODEL_FAST_FILTER` | `openai/gpt-oss-20b` | High-speed semantic filtering |
| `GROQ_MODEL_SYNTHESIS` | `openai/gpt-oss-120b` | Executive dossier & hypothesis synthesis |
| `DATABASE_URL` | `sqlite:///discovery_engine.db` | Embedded qualitative evidence database *(or add Railway Postgres plugin)* |
| `PORT` | `8000` *(Railway provides automatically)* | Internal container port |

---

### Step 1.5: Verify Railway Backend Deployment
Once the deployment finishes (Status: **Active** / **Online**), test your endpoints:

```bash
# 1. Health check
curl -s https://<your-railway-url>.up.railway.app/health

# Expected response:
# {"status":"healthy","app_name":"AI-Powered Discovery Engine...","groq_api_configured":true,"database_connected":true}

# 2. Swagger docs
curl -I https://<your-railway-url>.up.railway.app/docs
# Expected: HTTP/2 200

# 3. Overview API
curl -s https://<your-railway-url>.up.railway.app/api/v1/overview
```

---

## 4. Phase 2: Deploying Frontend to Vercel

### Step 2.1: Update `vercel.json` with Railway URL
In [`frontend/vercel.json`](file:///c:/Users/ADMIN/Desktop/PRODUCT%20OWNER%20PROJECT%203/AI%20Discovery%20Engine/frontend/vercel.json), replace `YOUR-RAILWAY-BACKEND-URL` with your actual Railway domain:

```json
{
  "version": 2,
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://ai-discovery-engine-production.up.railway.app/api/:path*"
    },
    {
      "source": "/health",
      "destination": "https://ai-discovery-engine-production.up.railway.app/health"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```
Commit and push this change to GitHub:
```powershell
git add frontend/vercel.json
git commit -m "chore: configure Vercel rewrite proxy to live Railway backend"
git push
```

---

### Step 2.2: Import Project in Vercel
1. Log into your **Vercel Dashboard** at [vercel.com](https://vercel.com/).
2. Click **`Add New...`** &rarr; **`Project`**.
3. Import your GitHub repository: `ai-discovery-engine`.

---

### Step 2.3: Configure Vercel Project Settings
In the **Configure Project** screen, configure the following:

| Setting | Value | Explanation |
| :--- | :--- | :--- |
| **Project Name** | `ai-discovery-engine` | Clean URL identifier |
| **Framework Preset** | **`Vite`** | Automatically detects Vite build tools |
| **Root Directory** | **`frontend`** | Click **Edit** and set to `frontend` subfolder |
| **Build Command** | `npm run build` | Compiles TypeScript and runs Vite production bundler |
| **Output Directory** | `dist` | Default Vite build destination |
| **Install Command** | `npm install` | Installs frontend dependencies |

---

### Step 2.4: Set Frontend Environment Variables
Under **Environment Variables**, add:

| Key | Value | Purpose |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | *(leave empty OR set to your Railway URL)* | Optional override; relative paths (`/api`) use Vercel rewrites |

---

### Step 2.5: Deploy
1. Click **`Deploy`**.
2. Vercel will build the frontend in ~25 seconds and assign a production URL:
   `https://ai-discovery-engine.vercel.app`

---

## 5. End-to-End Verification & Sanity Audit

Perform the following verification matrix after deployment:

| Check | Target / Endpoint | Expected Result |
| :--- | :--- | :--- |
| **1. UI Presentation** | `https://ai-discovery-engine.vercel.app/` | Loads dark/light dashboard, Recharts charts, Lucide icons |
| **2. Proxy Health** | `https://ai-discovery-engine.vercel.app/health` | HTTP `200 OK`, `status: "healthy"` |
| **3. API Overview** | `https://ai-discovery-engine.vercel.app/api/v1/overview` | Returns platform breakdown & evidence counts |
| **4. Problem Clusters** | `https://ai-discovery-engine.vercel.app/api/v1/clusters` | Returns 4 problem clusters with failure scores |
| **5. AI Copilot Query** | Submit question in AI Copilot tab | Streams response from Groq LPU via Railway backend |
| **6. CORS Validation** | Browser DevTools Console | Zero CORS errors, zero blocked requests |

---

## 6. Continuous Deployment & Monitoring

### Automated Git Workflows
- **Frontend Updates:** Any commit touching `frontend/**` triggers an automatic zero-downtime atomic preview or production deploy on Vercel.
- **Backend Updates:** Any commit touching `backend/**` triggers a rebuild of the Railway container and hot-swaps the running instance.

### Health Probes & Alerts
- Monitor container metrics (CPU, RAM, Network) directly in the **Railway Metrics tab**.
- Monitor page speed, CDN cache hit ratio, and web vitals in the **Vercel Analytics tab**.

---

## 7. Troubleshooting Quick Reference

### Issue A: Vercel displays "404 Not Found" on page refresh
- **Cause:** Client-side SPA routing not caught by static file server.
- **Resolution:** Ensure `frontend/vercel.json` includes the fallback rewrite rule:
  ```json
  { "source": "/(.*)", "destination": "/index.html" }
  ```

### Issue B: API calls return `502 Bad Gateway` on Vercel
- **Cause:** Railway backend container is booting or sleeping.
- **Resolution:** Check Railway logs for startup errors. Verify the Railway public URL matches the destination in `frontend/vercel.json`.

### Issue C: Database connections fail on Railway
- **Cause:** PostgreSQL URL misconfigured or SQLite path missing.
- **Resolution:** The engine includes automatic fallback to `discovery_engine.db`. If using PostgreSQL on Railway, add the PostgreSQL plugin in Railway and pass `${{Postgres.DATABASE_URL}}` as the `DATABASE_URL` environment variable.
