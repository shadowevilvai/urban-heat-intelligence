# Urban Heat Intelligence — Integration Checklist

Use this checklist before combining everyone's work.

## Phase 1 — Repository

- [ ] Everyone has cloned the same GitHub repository
- [ ] Everyone has access to `develop`
- [ ] Everyone has created a feature branch
- [ ] `main` is protected from accidental direct pushes
- [ ] `.gitignore` is committed
- [ ] `.env.example` is committed

## Phase 2 — Contracts

- [ ] API endpoints are documented
- [ ] Request schemas are documented
- [ ] Response schemas are documented
- [ ] Error responses are documented
- [ ] Frontend uses the documented API format
- [ ] ML/backend interfaces are documented
- [ ] Geospatial data format is documented
- [ ] Optimization input/output is documented

## Phase 3 — Individual Testing

### Frontend

- [ ] UI loads
- [ ] Map loads
- [ ] Mock data works
- [ ] API service layer works
- [ ] Loading states work
- [ ] Error states work
- [ ] Empty data states work

### Backend

- [ ] Server starts
- [ ] Health endpoint works
- [ ] API validation works
- [ ] Database connection works
- [ ] API tests pass
- [ ] CORS is configured for development

### ML

- [ ] Model loads
- [ ] Input format is correct
- [ ] Output format is correct
- [ ] Invalid input is handled
- [ ] Model endpoint/service works if applicable

### Geospatial

- [ ] Required data loads
- [ ] Coordinate system is correct
- [ ] Geometry is valid
- [ ] Output schema is correct

### Optimization

- [ ] Input schema is correct
- [ ] Simulation runs
- [ ] Optimization returns valid results
- [ ] Failure cases are handled

## Phase 4 — Integration

Test the complete path:

```text
Frontend
   ↓
API
   ↓
Database
   ↓
Geospatial / ML / Optimization
   ↓
API response
   ↓
Frontend visualization
```

Verify:

- [ ] Hotspots appear correctly
- [ ] Risk values are displayed correctly
- [ ] Map coordinates are correct
- [ ] API errors are handled
- [ ] Missing data does not crash the frontend
- [ ] Loading states work
- [ ] Simulation request works
- [ ] Optimization result appears correctly
- [ ] End-to-end demo scenario works

## Phase 5 — Merge

For each PR:

- [ ] Correct base branch = `develop`
- [ ] PR description completed
- [ ] Reviewer assigned
- [ ] Tests/build pass
- [ ] No secrets
- [ ] No unrelated changes
- [ ] API contract updated if needed
- [ ] Conflicts resolved
- [ ] Reviewer approves
- [ ] PR merged

## Phase 6 — Demo Freeze

Before the final demo:

- [ ] Stop feature development on the demo branch
- [ ] Run full integration test
- [ ] Verify environment variables
- [ ] Verify database
- [ ] Verify external APIs/data
- [ ] Verify map
- [ ] Verify ML results
- [ ] Verify optimization
- [ ] Verify fallback/error states
- [ ] Test on the actual demo laptop
- [ ] Test the internet/offline failure scenario where relevant
- [ ] Create a known-good release/tag
- [ ] Do not make untested changes after freeze
