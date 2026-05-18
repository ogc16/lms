# Deploy LMS to Digital Ocean App Platform

## Prerequisites

- A [Digital Ocean](https://cloud.digitalocean.com) account
- Your repo pushed to GitHub: `github.com/ogc16/lms`

## Steps

1. Go to https://cloud.digitalocean.com → **Apps** → **Create App**
2. Connect your GitHub repo (`ogc16/lms`)
3. DO detects `.do/app.yaml` and pre-configures 3 resources:
   - **Backend** — Docker service (port 8000) from `backend/Dockerfile`
   - **Frontend** — Docker service (port 80) from `frontend/Dockerfile`
   - **PostgreSQL** — managed database (`lms-db`)
4. When prompted, set `DJANGO_SECRET_KEY` to:
   ```
   -uuajfhr&czh*x$d=hpo%9$a5+d4h#4v5ljk&3a$ejis+u(u@y
   ```
5. Edit plan sizes (basic-xxs is fine for both services) → **Launch App**

## Post-Deployment

After deployment completes, update these env vars in the DO dashboard (**Settings → Backend/Frontend → Environment Variables**):

| Service | Variable | Value |
|---------|----------|-------|
| Backend | `CORS_ORIGINS` | `https://<frontend-url>.ondigitalocean.app` |
| Frontend | `BACKEND_URL` | `http://backend` (already set — internal DO DNS) |

The frontend reaches the backend via DO's internal DNS (`http://backend`), so no public exposure needed for the backend. The `DATABASE_URL` is auto-injected by the PostgreSQL service.

## Redeploy

Push to the `master` branch on GitHub → DO auto-deploys.
