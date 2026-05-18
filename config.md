Option 1: GitHub Integration (easiest)
1. 
Go to https://railway.app and log in with GitHub
2. 
Click New Project → Deploy from GitHub repo
3. 
Select your repo (ogc16/lms)
4. 
Railway will ask how many services — choose 2 services
5. 
Set root directories:
- 
Service 1: Root dir = backend/ (Django API) → Railway detects Dockerfile
- 
Service 2: Root dir = frontend/ (React SPA) → Railway detects Dockerfile
6. 
Add PostgreSQL plugin (Database → PostgreSQL)
7. 
Set environment variables on the backend service:
- 
DJANGO_SECRET_KEY → generate a random key (python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
- 
DEBUG → False
- 
CORS_ORIGINS → https://your-frontend-url.up.railway.app
8. 
Set environment variables on the frontend service:
- 
BACKEND_URL → https://your-backend-url.up.railway.app
Railway will auto-deploy. The PostgreSQL env vars (PGHOST, etc.) are injected automatically by the plugin.
Option 2: Railway CLI
npm i -g @railway/cli
railway login
railway init
railway add postgresql
railway up

## Render
Committed and pushed. Here's how to deploy on Render:
1. 
Go to https://dashboard.render.com → New + → Blueprint
2. 
Connect your ogc16/lms GitHub repo
3. 
Render reads render.yaml and creates 3 resources:
- 
PostgreSQL database (free tier)
- 
lms-backend Web Service (Docker, mcwein/lms-backend:latest)
- 
lms-frontend Web Service (Docker, mcwein/lms-frontend:latest)
4. 
When prompted, set DJANGO_SECRET_KEY to -uuajfhr&czh*x$d=hpo%9$a5+d4h#4v5ljk&3a$ejis+u(u@y
5. 
After deployment, update the CORS_ORIGINS on the backend and BACKEND_URL on the frontend with the actual .onrender.com URLs (they appear in the dashboard)
Render auto-provisions the database URL and injects it as DATABASE_URL into the backend. The ALLOWED_HOSTS and RENDER_EXTERNAL_URL are handled automatically by the code.
## Digital Ocean 
Deployment to Digital Ocean App Platform is set up. Here's what to do:
1. 
Go to https://cloud.digitalocean.com → Apps → Create App
2. 
Connect your GitHub repo (ogc16/lms)
3. 
DO detects .do/app.yaml and pre-configures:
- 
Backend service (Dockerfile at backend/Dockerfile, port 8000)
- 
Frontend service (Dockerfile at frontend/Dockerfile, port 80)
- 
PostgreSQL database (lms-db)
4. 
Set DJANGO_SECRET_KEY when prompted: -uuajfhr&czh*x$d=hpo%9$a5+d4h#4v5ljk&3a$ejis+u(u@y
5. 
Deploy
After deployment, update these env vars in the DO dashboard:
Service	Variable	Value
Backend	CORS_ORIGINS	https://<actual-frontend-url>.ondigitalocean.app
Frontend	BACKEND_URL	http://backend (internal, already set — change if needed)
The frontend reaches the backend internally via http://backend (DO's internal DNS). The DATABASE_URL is auto-injected by DO from the PostgreSQL service.