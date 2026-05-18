# Deploy LMS

## Prerequisites

- Docker images on Docker Hub: `mcwein/lms-backend:latest`, `mcwein/lms-frontend:latest`
- Source code on GitHub: `github.com/ogc16/lms`
- Django secret key: `-uuajfhr&czh*x$d=hpo%9$a5+d4h#4v5ljk&3a$ejis+u(u@y`

---

## 1. Vercel (Frontend) + Backend (any provider)

**Best for:** Free frontend hosting on Vercel + backend hosted anywhere.

Deploy the frontend to Vercel and the backend separately on any service that can run Docker or Django.

### Frontend → Vercel

1. Push to GitHub → go to https://vercel.com → **Add New Project** → Import `ogc16/lms`
2. Set **Root Directory** to `frontend`
3. Under **Environment Variables**, add:
   - `VITE_API_URL` → `https://<your-backend-url>` (the public backend URL)
4. **Deploy** — Vercel auto-detects Vite and builds the SPA

The frontend's `client.ts` reads `VITE_API_URL` at build time. Any `/api/...` request goes directly to the backend URL.

### Backend → pick one

With the frontend on Vercel, the backend just needs a public HTTPS URL and CORS configured. Options:

| Provider | Cost | Setup |
|----------|------|-------|
| **Render** | Free | Docker image `mcwein/lms-backend:latest` + PostgreSQL (free) |
| **Fly.io** | Free | `fly launch` with Docker |
| **Google Cloud Run** | Free tier | Serverless Docker, pay-per-use |
| **Any VPS** | $4-12/mo | `docker compose up -d` |
| **PythonAnywhere** | Free–$5 | Manual Django + `gunicorn` |

### Config for any backend provider

```env
DJANGO_SECRET_KEY=-uuajfhr&czh*x$d=hpo%9$a5+d4h#4v5ljk&3a$ejis+u(u@y
DEBUG=False
ALLOWED_HOSTS=.ondigitalocean.app,.onrender.com,.fly.dev,.run.app,yourdomain.com,localhost
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

If using a Docker-based provider, use `mcwein/lms-backend:latest` and add a PostgreSQL database. If going without Docker, follow the **Django directly** section below.

---

## 2. Digital Ocean App Platform

**Best for:** Zero server management, auto HTTPS, auto-deploy on git push.

1. Go to https://cloud.digitalocean.com → **Apps** → **Create App**
2. Connect your GitHub repo (`ogc16/lms`)
3. DO detects `.do/app.yaml` and pre-configures:
   - **Backend** — Docker service (port 8000) from `backend/Dockerfile`
   - **Frontend** — Docker service (port 80) from `frontend/Dockerfile`
   - **PostgreSQL** — managed database (`lms-db`)
4. Set `DJANGO_SECRET_KEY` when prompted
5. **Launch App**

**Post-deploy:** Set `CORS_ORIGINS` on backend to the actual frontend `.ondigitalocean.app` URL.

**Redeploy:** Push to `master` → auto-deploys.

> **Cost:** ~$24/mo (basic-xxs × 2 services + $0 for database on basic plan). Free tier not available.

---

## 3. Render

**Best for:** Free tier, simple setup, auto HTTPS.

1. Go to https://dashboard.render.com → **New +** → **Blueprint**
2. Connect `ogc16/lms` repo
3. Render reads `render.yaml` and creates:
   - **PostgreSQL** (free tier)
   - **lms-backend** — Web Service (Docker image `mcwein/lms-backend:latest`)
   - **lms-frontend** — Web Service (Docker image `mcwein/lms-frontend:latest`)
4. Set `DJANGO_SECRET_KEY` when prompted
5. **Deploy**

**Post-deploy:**
- Set `BACKEND_URL` on frontend to `https://<backend-url>.onrender.com`
- Set `CORS_ORIGINS` on backend to `https://<frontend-url>.onrender.com`

**Redeploy:** Push to master → auto-deploys (blueprint) or manual deploy from dashboard (Docker image).

> **Cost:** Free tier available (services spin down after inactivity). $7/mo each for no spin-down.

---

## 4. Google Cloud Run

**Best for:** Serverless, auto-scaling, pay-per-use, generous free tier.

Deploy the backend Docker image to Cloud Run. Use a managed PostgreSQL database from Cloud SQL or a cheaper alternative like [Neon](https://neon.tech) (serverless Postgres, free tier).

### Backend → Cloud Run

1. Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install) and authenticate:
   ```bash
   gcloud auth login
   gcloud config set project <your-project-id>
   ```

2. Enable required services:
   ```bash
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com
   ```

3. Create an Artifact Registry repository and push the Docker image:
   ```bash
   gcloud artifacts repositories create lms-repo --repository-format=docker --location=us-central1
   docker tag mcwein/lms-backend:latest us-central1-docker.pkg.dev/<project>/lms-repo/lms-backend:latest
   docker push us-central1-docker.pkg.dev/<project>/lms-repo/lms-backend:latest
   ```

4. Deploy to Cloud Run:
   ```bash
   gcloud run deploy lms-backend \
     --image us-central1-docker.pkg.dev/<project>/lms-repo/lms-backend:latest \
     --region us-central1 \
     --allow-unauthenticated \
     --cpu=1 --memory=512Mi \
     --min-instances=0 --max-instances=2 \
     --set-env-vars="DJANGO_SECRET_KEY=-uuajfhr&czh*x$d=hpo%9$a5+d4h#4v5ljk&3a$ejis+u(u@y" \
     --set-env-vars="DEBUG=False" \
     --set-env-vars="ALLOWED_HOSTS=.run.app,localhost" \
     --set-env-vars="CORS_ORIGINS=https://<your-frontend-url>" \
     --set-env-vars="DATABASE_URL=<your-postgres-connection-string>" \
     --port=8000
   ```

   Cloud Run injects the `PORT` env var automatically — the Dockerfile's `CMD` picks it up.

### Full-stack: deploy both frontend and backend

Running both services on Cloud Run gives you auto-scaling HTTPS on a single platform.

1. Push the frontend image to Artifact Registry:
   ```bash
   docker tag mcwein/lms-frontend:latest us-central1-docker.pkg.dev/<project>/lms-repo/lms-frontend:latest
   docker push us-central1-docker.pkg.dev/<project>/lms-repo/lms-frontend:latest
   ```

2. Deploy the backend (see steps above) and note its `.run.app` URL.

3. Deploy the frontend:
   ```bash
   gcloud run deploy lms-frontend \
     --image us-central1-docker.pkg.dev/<project>/lms-repo/lms-frontend:latest \
     --region us-central1 \
     --allow-unauthenticated \
     --cpu=1 --memory=256Mi \
     --min-instances=0 --max-instances=2 \
     --set-env-vars="BACKEND_URL=https://lms-backend-xxxxx-uc.a.run.app" \
     --port=80
   ```

4. Update the backend's `CORS_ORIGINS` to the frontend's `.run.app` URL:
   ```bash
   gcloud run deploy lms-backend --image ... --region us-central1 \
     --set-env-vars="CORS_ORIGINS=https://lms-frontend-xxxxx-uc.a.run.app" \
     --update-env-vars="ALLOWED_HOSTS=.run.app,localhost" \
     --set-env-vars="DJANGO_SECRET_KEY=..." \
     --set-env-vars="DEBUG=False" \
     --set-env-vars="DATABASE_URL=..."
   ```

**How it works:** The frontend SPA makes API calls to `/api/...` (same origin). Nginx on the frontend container proxies those to the backend via `BACKEND_URL`. No `VITE_API_URL` needed — the `client.ts` falls back to `/api`.

### Database options

### Redeploy

```bash
docker build -t mcwein/lms-backend:latest ./backend
docker tag mcwein/lms-backend:latest us-central1-docker.pkg.dev/<project>/lms-repo/lms-backend:latest
docker push us-central1-docker.pkg.dev/<project>/lms-repo/lms-backend:latest
gcloud run deploy lms-backend --image us-central1-docker.pkg.dev/<project>/lms-repo/lms-backend:latest --region us-central1
```

> **Cost:** Free tier (2M requests, 1 GB outbound, 360k GB-seconds per month). Overages are minimal for low traffic.

---

## 5. Docker on any VPS (Linux)

**Best for:** Full control, lowest cost, any cloud provider.

1. Provision a Linux VM (Ubuntu 22.04+) with Docker & Docker Compose.
   *Cheap options: $4-6/mo (Hetzner, RackNerd) or free (Oracle Cloud always-free tier).*

2. SSH into the server and clone the repo:
   ```bash
   git clone https://github.com/ogc16/lms.git
   cd lms
   ```

3. Edit `docker-compose.yml` to use Docker Hub images instead of building locally:
   ```yaml
   services:
     db:
       image: postgres:16-alpine
       volumes:
         - postgres_data:/var/lib/postgresql/data
       environment:
         POSTGRES_DB: lms
         POSTGRES_USER: lms_user
         POSTGRES_PASSWORD: changeme123
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U lms_user -d lms"]
         interval: 5s
         timeout: 5s
         retries: 5

     backend:
       image: mcwein/lms-backend:latest
       environment:
         DJANGO_SECRET_KEY: <your-secret-key>
         DEBUG: "False"
         DB_ENGINE: django.db.backends.postgresql
         DB_NAME: lms
         DB_USER: lms_user
         DB_PASSWORD: changeme123
         DB_HOST: db
         DB_PORT: 5432
         ALLOWED_HOSTS: .your-domain.com,localhost
         CORS_ORIGINS: https://your-domain.com
       depends_on:
         db:
           condition: service_healthy

     frontend:
       image: mcwein/lms-frontend:latest
       ports:
         - "80:80"
         - "443:443"
       environment:
         BACKEND_URL: http://backend:8000
       depends_on:
         - backend

   volumes:
     postgres_data:
   ```

4. Start the stack:
   ```bash
   docker compose up -d
   ```

5. Set up Nginx reverse proxy & SSL (using Certbot) to point `your-domain.com` → `localhost:80`.

6. Create a superuser:
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

**Redeploy:** Pull new Docker images and restart:
```bash
docker compose pull && docker compose up -d
```

> **Cost:** $4-12/mo for VPS + domain (optional). Free options: Oracle Cloud, Google Cloud free tier.

---

## 6. Django directly (without Docker)

**Best for:** Simple single-server setup, minimal overhead.

1. Provision a Linux VM (Ubuntu 22.04+) with Python 3.12, PostgreSQL, Nginx.

2. Clone and set up the backend:
   ```bash
   git clone https://github.com/ogc16/lms.git
   cd lms/backend

   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt gunicorn

   cp .env.example .env
   # Edit .env with your DB credentials and secret key

   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

3. Set up Gunicorn as a systemd service (`/etc/systemd/system/lms-backend.service`):
   ```ini
   [Unit]
   Description=LMS Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/opt/lms/backend
   EnvironmentFile=/opt/lms/backend/.env
   ExecStart=/opt/lms/backend/.venv/bin/gunicorn lms_project.wsgi:application --workers 3 --bind 0.0.0.0:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. Build and serve the frontend:
   ```bash
   cd ../frontend
   npm install && npm run build
   # Copy dist/ to /var/www/lms/
   ```

5. Configure Nginx (`/etc/nginx/sites-available/lms`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       root /var/www/lms;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api/ {
           proxy_pass http://127.0.0.1:8000/api/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /admin/ {
           proxy_pass http://127.0.0.1:8000/admin/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static/ {
           alias /opt/lms/backend/staticfiles;
       }
   }
   ```

6. Enable and restart:
   ```bash
   systemctl enable lms-backend
   systemctl start lms-backend
   ln -s /etc/nginx/sites-available/lms /etc/nginx/sites-enabled/
   nginx -t && systemctl reload nginx
   ```

7. Set up SSL with Certbot:
   ```bash
   certbot --nginx -d your-domain.com
   ```

**Redeploy:** Pull latest code and restart:
```bash
cd /opt/lms && git pull
# Backend
cd backend && source .venv/bin/activate && pip install -r requirements.txt
python manage.py migrate && python manage.py collectstatic --noinput
systemctl restart lms-backend
# Frontend
cd ../frontend && npm install && npm run build && cp -r dist/* /var/www/lms/
```

> **Cost:** $4-12/mo for VPS + domain (optional). Same as VPS but without Docker overhead.

---

## Comparison

| Method | Difficulty | Cost/mo | Auto HTTPS | Auto-deploy | Managed DB |
|--------|-----------|---------|------------|-------------|------------|
| Vercel + Render | Easy | Free | Yes | Yes | Yes |
| Vercel + Cloud Run + Neon | Medium | Free | Yes | Manual | Yes |
| Cloud Run (both) | Medium | Free tier | Yes | Manual | External |
| DO App Platform | Easy | ~$24 | Yes | Yes (git push) | Yes |
| Render (all-in-one) | Easy | Free–$14 | Yes | Yes | Yes |
| Docker on VPS | Medium | $4–12 | Manual (Certbot) | No (pull) | No |
| Django directly | Medium | $4–12 | Manual (Certbot) | No (pull) | No |

## Environment Variables Reference

| Variable | Backend | Frontend | Description |
|----------|---------|----------|-------------|
| `DJANGO_SECRET_KEY` | Required | — | Django secret (use provided key) |
| `DEBUG` | Required | — | Set to `False` in production |
| `ALLOWED_HOSTS` | Required | — | Comma-separated allowed hosts |
| `CORS_ORIGINS` | Required | — | Comma-separated frontend URLs |
| `DATABASE_URL` | Optional | — | Full PostgreSQL connection string |
| `BACKEND_URL` | — | Required | Backend URL (internal or public) |
