# Urban Heat Intelligence — Developer Setup Guide

## Read This First

This document is for every team member who needs to run the project on their own computer.

The team should maintain one source of truth in the GitHub repository. Do not send project folders manually between teammates.

Some commands below depend on the exact dependencies currently committed in the repository. If the repository's README/package files specify a different version, follow the repository's version.

---

# 1. Install Required Software

Recommended baseline:

### Everyone

- Git
- VS Code or another IDE
- GitHub account with repository access

### Frontend developer

- Node.js LTS
- npm (or the package manager specified by the repository)

### Backend / ML / Geospatial / Optimization

- Python 3.11+ unless the repository specifies another version
- pip
- Python virtual environment support

### Database

If the project uses PostgreSQL/PostGIS, use the team's shared development database or the Docker setup provided by the repository.

Do not create a different schema manually unless instructed.

---

# 2. Verify Installation

Run:

```bash
git --version
```

Frontend developer:

```bash
node --version
npm --version
```

Python developers:

```bash
python --version
pip --version
```

If Windows uses `py`:

```bash
py --version
```

---

# 3. Clone the Project

Get the repository URL from the team lead.

```bash
git clone YOUR_REPOSITORY_URL
```

Enter the project:

```bash
cd YOUR_REPOSITORY_FOLDER
```

Check:

```bash
git remote -v
```

You should see the GitHub repository as `origin`.

---

# 4. Get the Latest Integration Code

```bash
git fetch --all
git checkout develop
git pull origin develop
```

Do not start feature work directly on `develop`.

Create your feature branch:

```bash
git checkout -b feature/YOUR-FEATURE
```

Example:

```bash
git checkout -b feature/frontend-dashboard
```

---

# 5. Frontend Setup

Go into the frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create local environment variables if required:

```text
.env
```

Use `.env.example` as the template.

Example:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The exact variable name must match the project's frontend code.

Start the frontend:

```bash
npm run dev
```

The terminal will show the local development URL.

Do not assume the port is always 5173; use the URL printed by the project.

---

# 6. Backend Setup

Open another terminal.

Go to:

```bash
cd backend
```

Create a virtual environment.

Windows:

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If the repository uses `pyproject.toml` instead of `requirements.txt`, follow its documented installation command.

Create `.env` from `.env.example`.

Example:

```env
DATABASE_URL=
MODEL_API_URL=
```

Start the backend using the command specified by the repository.

For a standard FastAPI setup, this may be:

```bash
uvicorn app.main:app --reload
```

The backend will normally expose something similar to:

```text
http://localhost:8000
```

---

# 7. Database Setup

The application should document one of these approaches:

### Option A — Shared development database

Everyone uses the same development database URL supplied by the team lead.

### Option B — Local database

Each developer runs PostgreSQL/PostGIS locally.

### Option C — Docker

The repository provides a Docker Compose configuration.

If the project contains:

```text
docker-compose.yml
```

follow the commands in the repository README.

Do not invent database credentials.

---

# 8. ML Setup

Go to:

```bash
cd ml
```

Activate the project's Python environment.

Install dependencies using the repository's requirements file or documented setup.

Example:

```bash
pip install -r requirements.txt
```

Run the model/service using the project's documented command.

If the ML component is not a separate service and is imported by the backend, do not start a second server unless the repository says to.

---

# 9. Geospatial Setup

The geospatial component may require:

- raster/vector libraries
- GDAL
- GeoPandas
- Rasterio
- Shapely
- satellite-data access
- PostGIS

Do not install random system packages without checking the project's setup instructions.

If the repository provides Docker or a requirements/lock file, use that environment.

---

# 10. Optimization Setup

The optimization component should have its own dependency list if it is separated from backend/ML.

Install from the repository's dependency definition.

The optimization service should communicate through the agreed interface rather than directly modifying frontend code.

---

# 11. Running the Whole System Locally

A typical development setup may look like:

### Terminal 1 — Frontend

```bash
cd frontend
npm run dev
```

### Terminal 2 — Backend

```bash
cd backend
# activate .venv
uvicorn app.main:app --reload
```

### Terminal 3 — ML

Only if ML is a separate service:

```bash
cd ml
# project-specific command
```

### Terminal 4 — Geospatial

Only if geospatial is a separate service:

```bash
cd geospatial
# project-specific command
```

### Terminal 5 — Optimization

Only if optimization is a separate service:

```bash
cd optimization
# project-specific command
```

The exact commands should be added to the repository README once the architecture is finalized.

---

# 12. Frontend ↔ Backend Connection

During development:

```text
Browser
   |
   | HTTP
   ↓
Frontend
   |
   | API request
   ↓
Backend
   |
   +---- Database
   +---- ML
   +---- Geospatial
   +---- Optimization
```

If the backend is running on your own machine:

```env
VITE_API_BASE_URL=http://localhost:8000
```

If a shared development API is available:

```env
VITE_API_BASE_URL=https://YOUR-DEV-API
```

Do not hard-code the development URL into dozens of frontend components.

Keep it in the environment/configuration layer.

---

# 13. Mock API Development

The frontend developer can work before the backend is complete.

Use data matching the API contract:

```json
{
  "hotspots": [
    {
      "id": "hs-001",
      "latitude": 19.01,
      "longitude": 72.84,
      "lst_celsius": 42.7,
      "severity": "high"
    }
  ]
}
```

When the real API is ready, switch the data source/configuration.

The UI should not need to be rebuilt.

---

# 14. CORS

If the browser reports a CORS error such as:

```text
Access to fetch ... has been blocked by CORS policy
```

do not "fix" it by disabling browser security.

The backend should explicitly allow the development frontend origin.

For example, the backend may allow:

```text
http://localhost:5173
```

if that is the actual frontend URL.

The exact CORS configuration belongs to the backend.

---

# 15. Common Problems

## `git` is not recognized

Install Git and restart the terminal.

## `npm` is not recognized

Install Node.js LTS and restart the terminal.

## Python command not found

Install Python and make sure it is available in PATH.

## Dependencies fail

First check:

```bash
git pull origin develop
```

Then install using the project's lockfile/requirements.

Do not randomly upgrade every package.

## Port already in use

Find the process using the port or change the development port according to the project's configuration.

## Frontend cannot reach backend

Check:

1. Backend is actually running.
2. Frontend API URL is correct.
3. Backend port is correct.
4. CORS is configured.
5. `.env` was loaded correctly.
6. You restarted the frontend after changing environment variables.

## Database connection failed

Check:

1. Database is running.
2. `DATABASE_URL` is correct.
3. Database credentials are correct.
4. The required PostGIS extension/schema exists.
5. You are using the correct development database.

---

# 16. Before Saying "It Works"

Run:

```bash
git status
```

Then confirm:

- application starts
- required API calls work
- no console errors
- no secrets are staged
- feature works with a clean checkout
- tests/build pass where available

Then commit:

```bash
git add .
git commit -m "feat: YOUR FEATURE"
git push -u origin feature/YOUR-FEATURE
```

---

# 17. Never Commit These

```text
.env
.env.local
node_modules/
.venv/
venv/
__pycache__/
*.pyc
dist/
build/
coverage/
*.log
large raw datasets
temporary files
private credentials
API keys
database passwords
```

These should be covered by `.gitignore`.

---

# 18. First-Day Checklist

Every team member should be able to check all of these:

- [ ] Git installed
- [ ] GitHub access confirmed
- [ ] Repository cloned
- [ ] `develop` checked out
- [ ] Project dependencies installed
- [ ] `.env` created locally
- [ ] Frontend/backend environment starts as applicable
- [ ] Development database connection works if required
- [ ] No secrets committed
- [ ] Personal feature branch created
- [ ] Test commit successfully pushed
- [ ] Team lead knows the developer is ready
