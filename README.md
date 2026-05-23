# Bug Hunter

Educational tool for Python bug-fixing. Students are shown broken Python snippets and must fix them in-browser using a Monaco editor with Pyodide-powered test execution.

## Development

### Prerequisites

- Docker (for PostgreSQL)
- Python 3.12+
- Node.js 18+

### First-time setup

**1. Configure environment**

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:
- `SECRET_KEY` — any long random string for local dev
- `OPENAI_BASE_URL` — your LLM endpoint (e.g. `https://promptlyapi.com/v1`)
- `OPENAI_MODEL` — model name your endpoint accepts
- `OPENAI_API_KEY` — your API key

**2. Start PostgreSQL**

```bash
docker compose up db -d
```

The `docker-compose.override.yml` exposes the DB on `localhost:5433` (port 5432 is reserved for other services on this machine).

**3. Install backend dependencies**

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**4. Run database migrations**

```bash
cd backend
.venv/bin/alembic upgrade head
```

**5. Install frontend dependencies**

```bash
cd frontend
npm install
```

### Running locally

In one terminal, start the backend:

```bash
/home/siderealyear/bug-hunter/backend/.venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 --port 8000 --reload \
  --app-dir /home/siderealyear/bug-hunter/backend
```

In another terminal, start the frontend:

```bash
cd frontend
npm run dev
```

Open **http://localhost:5173**. The Vite dev server proxies all `/api/*` requests to the backend on port 8000.

The backend API docs are available at **http://localhost:8000/docs**.

### Creating the first admin account

```bash
# Insert a test invite code directly into the DB
PGPASSWORD=bughunter psql -h localhost -p 5433 -U bughunter bughunter \
  -c "INSERT INTO invite_codes (code, is_active) VALUES ('test123', true);"

# Register via the API
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123","invite_code":"test123"}' \
  | python3 -m json.tool

# Promote the user to admin
PGPASSWORD=bughunter psql -h localhost -p 5433 -U bughunter bughunter \
  -c "UPDATE \"user\" SET is_admin = true WHERE email = 'admin@example.com';"
```

Then log in at http://localhost:5173/login and use the **Admin → Generate** panel to test the LLM pipeline.

## Deployment

### Overview

The project uses two environments hosted on gatekeeper:

| Environment | URL | Port |
|---|---|---|
| Staging | `http://100.64.0.1:8507` (Tailnet only) | 8507 |
| Production | `https://bug-hunter.perdrizet.org` | 8509 (proxied by nginx) |

### CI/CD Workflows

**Tests** (`test.yml`) — runs on every pull request to `main`:
- `lint-backend`: ruff lint check of the backend
- `typecheck-frontend`: `npm run build` (runs `tsc -b`)

Both jobs must pass before a PR can be merged.

**Deploy Staging** (`deploy-staging.yml`) — runs automatically on every push to `main`:
- SSHs into gatekeeper, pulls latest code to `/opt/bug-hunter-staging/`
- Builds and starts containers with `docker compose -f docker-compose.yml -f docker-compose.staging.yml up --build -d`
- Health checks `http://100.64.0.1:8507/api/health`

**Deploy Production** (`deploy-prod.yml`) — manual dispatch only:
- Requires `version` (e.g. `v0.1.0`) and `confirm` set to `deploy`
- SSHs into gatekeeper, pulls latest code to `/opt/bug-hunter/`
- Builds and starts containers with `docker compose up --build -d`
- Health checks `http://127.0.0.1:8509/api/health`
- Creates a git tag and GitHub release

### Server Setup

The host nginx on gatekeeper reverse proxies `bug-hunter.perdrizet.org` → `127.0.0.1:8509`. The nginx config lives in `vps-infrastructure/configs/nginx/conf.d/bug-hunter.conf`.

Each environment needs a `.env` file on the server (not committed to git):

```
DATABASE_URL=postgresql+asyncpg://bughunter:bughunter@db:5432/bughunter
SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_hex(32))">
LLM_PROVIDER=openai
OPENAI_BASE_URL=<your LLM endpoint>
OPENAI_MODEL=<model name>
OPENAI_API_KEY=<your API key>
CORS_ORIGINS=["https://bug-hunter.perdrizet.org"]   # or http://100.64.0.1:8507 for staging
```

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `GATEKEEPER_HOST` | Public IP of the server |
| `GATEKEEPER_USER` | SSH login username |
| `GATEKEEPER_SSH_KEY` | Private key with access to gatekeeper (no passphrase) |

