# Urban Heat Intelligence — Git/GitHub Team Workflow

## 1. Repository Structure

Recommended structure:

```text
urban-heat-intelligence/
│
├── frontend/                 # Frontend application
├── backend/                  # FastAPI/API/backend
├── ml/                       # ML/risk models
├── geospatial/               # Satellite/GIS/LST/NDVI processing
├── optimization/             # Simulation/optimization logic
├── docs/                     # Project documentation
│
├── .env.example
├── .gitignore
├── README.md
└── TEAM_START_HERE.md
```

The exact folder names can be changed by the team lead, but the ownership boundaries should remain clear.

---

# 2. Branch Strategy

Use:

```text
main
  |
  +-- develop
        |
        +-- feature/frontend-dashboard
        +-- feature/backend-api
        +-- feature/ml-risk
        +-- feature/geospatial
        +-- feature/optimization
```

### Meaning

- `main`: stable version used for final demo/deployment.
- `develop`: integration branch where completed team features are combined.
- `feature/*`: personal work.

Do not create random branches such as:

```text
test123
new
final
final2
latest
saurabh-new-final
```

Use descriptive names.

Examples:

```text
feature/frontend-map
feature/backend-hotspot-api
feature/ml-risk-model
fix/frontend-map-popup
fix/backend-validation
```

---

# 3. First-Time Setup

After receiving repository access:

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_FOLDER
```

Then check:

```bash
git branch
git remote -v
```

Fetch all branches:

```bash
git fetch --all
```

Switch to `develop`:

```bash
git checkout develop
```

Pull the latest version:

```bash
git pull origin develop
```

Now create your personal branch:

```bash
git checkout -b feature/YOUR-FEATURE
```

Example:

```bash
git checkout -b feature/frontend-dashboard
```

---

# 4. Daily Workflow

Every time you start working:

```bash
git checkout develop
git pull origin develop
git checkout feature/YOUR-FEATURE
```

If your feature branch already exists:

```bash
git checkout feature/YOUR-FEATURE
```

Then code normally.

---

# 5. Save Your Work

Check what changed:

```bash
git status
```

Review the files:

```bash
git diff
```

Stage the changes:

```bash
git add .
```

Commit:

```bash
git commit -m "feat: add hotspot map"
```

Push:

```bash
git push -u origin feature/YOUR-FEATURE
```

For later pushes:

```bash
git push
```

---

# 6. Commit Message Rules

Use:

```text
feat: ...
fix: ...
refactor: ...
docs: ...
test: ...
chore: ...
```

Examples:

```text
feat: add hotspot map
feat: add heat risk endpoint
fix: handle missing satellite values
fix: prevent map crash on empty data
docs: update API contract
test: add hotspot endpoint tests
```

Avoid:

```text
changes
done
final
updated
asdf
working
```

---

# 7. Pull Request Process

When your feature works:

1. Push your branch.
2. Open GitHub.
3. Create a Pull Request.
4. Base branch = `develop`.
5. Compare branch = your feature branch.
6. Explain what you changed.
7. Explain how you tested it.
8. Request review from the appropriate teammate/team lead.

Example:

```text
Base:    develop
Compare: feature/frontend-dashboard
```

Do NOT open a PR directly into `main` unless the team lead explicitly requests it.

---

# 8. Before Opening a PR

Run the project's tests/build/linter.

At minimum:

```bash
git status
```

Make sure you did not accidentally include:

```text
.env
node_modules/
venv/
__pycache__/
dist/
build/
*.log
large datasets
model checkpoints
personal files
```

Then verify the app still runs.

---

# 9. Keeping Your Feature Branch Updated

If `develop` has changed while you were working:

```bash
git checkout develop
git pull origin develop
git checkout feature/YOUR-FEATURE
```

Then update your branch.

For a simple team workflow, merge `develop` into your feature branch:

```bash
git merge develop
```

If conflicts appear, resolve them carefully.

Then:

```bash
git add .
git commit -m "chore: sync with develop"
git push
```

The team can later move to rebase if everyone becomes comfortable with Git. Do not introduce rebase rules halfway through the project.

---

# 10. Merge Conflict Rule

If Git says:

```text
CONFLICT
```

DO NOT:

- delete random files
- copy someone's whole folder over yours
- use force push blindly
- ask everyone to reset the repository

Instead:

1. Read the conflicting file.
2. Identify what both people changed.
3. Keep the correct parts from both sides.
4. Run the application/tests.
5. Stage the resolved file.
6. Complete the merge.

If you are unsure, ask the person who owns that file.

---

# 11. API Change Rule

The frontend, backend, ML and geospatial components communicate through agreed interfaces.

Example:

```text
GET /api/v1/hotspots
```

If the response is:

```json
{
  "hotspots": [
    {
      "id": "hs-001",
      "latitude": 19.01,
      "longitude": 72.84,
      "severity": "high"
    }
  ]
}
```

do not suddenly change it to:

```json
{
  "data": [...]
}
```

without telling the frontend developer.

Any breaking API change must update:

```text
API_CONTRACT.md
```

and the affected developers must be informed before merging.

---

# 12. Frontend Development

Frontend should initially be able to work with mock data.

Example:

```text
Frontend
   |
   +-- Mock API / JSON
```

Later:

```text
Frontend
   |
   +-- Development API
           |
           +-- Backend
                   |
                   +-- Database
                   +-- ML
                   +-- Geospatial
                   +-- Optimization
```

This allows frontend development to continue even when backend/model work is incomplete.

---

# 13. Backend Development

Backend owns API implementation and should expose stable endpoints.

Recommended responsibility:

```text
Frontend
   ↓
FastAPI
   ↓
Services
   ↓
PostgreSQL/PostGIS
   ↓
ML / Geospatial / Optimization modules
```

The frontend should NOT connect directly to PostgreSQL.

---

# 14. Database Rules

Database schema changes must be documented.

Prefer migrations instead of manually changing a shared database.

Example migration process:

```text
Change schema
     ↓
Create migration
     ↓
Test migration
     ↓
Commit migration
     ↓
PR
```

Never commit a production database dump containing secrets or private information.

---

# 15. Environment Variables

Commit:

```text
.env.example
```

Do NOT commit:

```text
.env
```

Example:

```env
API_BASE_URL=
DATABASE_URL=
MODEL_API_URL=
MAP_API_KEY=
```

The example file contains variable names only, not secret values.

Each developer creates their own local `.env`.

---

# 16. What Each Person Owns

| Area | Primary Owner |
|---|---|
| Frontend/UI | Frontend developer |
| API/backend | Backend developer |
| ML/risk model | ML developer |
| Satellite/GIS processing | Geospatial developer |
| Simulation/optimization | Optimization developer |
| Integration/demo | Team lead + all developers |

Ownership does not mean other people cannot review the code. It means the owner should be consulted before changing important files in that area.

---

# 17. Definition of Done

A feature is NOT done just because the code works on one laptop.

Before PR:

- Code runs locally
- No secrets committed
- No unnecessary generated files
- Tests/build/lint pass where available
- API contract updated if necessary
- README/docs updated if necessary
- Feature branch pushed
- PR opened against `develop`
- Reviewer understands what changed

---

# 18. Emergency Rule

If something breaks after a merge:

```text
STOP adding random fixes.
```

First identify:

```text
Which PR?
Which commit?
Which component?
Can it be reverted safely?
```

Then fix the actual problem.

Do not keep stacking untested fixes on top of a broken integration branch.
