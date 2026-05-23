# Bug Hunter

[![Tests](https://github.com/gperdrizet/bug-hunter/actions/workflows/test.yml/badge.svg)](https://github.com/gperdrizet/bug-hunter/actions/workflows/test.yml)
[![Deploy Staging](https://github.com/gperdrizet/bug-hunter/actions/workflows/deploy-staging.yml/badge.svg)](https://github.com/gperdrizet/bug-hunter/actions/workflows/deploy-staging.yml)
[![Deploy Production](https://github.com/gperdrizet/bug-hunter/actions/workflows/deploy-prod.yml/badge.svg)](https://github.com/gperdrizet/bug-hunter/actions/workflows/deploy-prod.yml)

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

```bash
cp .env.example .env
# Edit .env with production values
docker compose --profile production up -d --build
```

The `docker-compose.override.yml` suppresses the backend and frontend containers during local dev. Pass `--profile production` to include them for a full stack deployment.

