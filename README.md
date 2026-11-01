# Graphene Trace

A pressure-monitoring platform for preventing pressure injuries. It ingests 32×32 pressure-sensor frames, analyses them for risk and movement, and shows clinicians and patients a live heatmap, metrics and alerts.

## Features

- **Pressure heatmaps** rendered from 32×32 sensor frames
- **Metrics and risk scoring** for each patient, including movement and posture analysis
- **Alerts** raised when pressure stays high, with comment threads for follow-up
- **Role-based access** for `patient` and `clinician` users, using JWT authentication
- Redis caching and rate limiting on the API

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy 2, Alembic, Pydantic |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Frontend | React 18, TypeScript, Vite, TanStack Query, Plotly |
| Deployment | Docker Compose, Fly.io (API), Netlify (frontend) |

## Getting started

### Option 1: Docker (recommended)

Starts PostgreSQL, Redis and the API with hot reload:

```bash
docker compose up --build
```

- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs

Run the frontend separately:

```bash
cd frontend
npm install
npm run dev     # http://localhost:5173
```

### Option 2: Run the backend locally

Requires Python 3.11+, PostgreSQL and Redis.

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head             # create the database schema
uvicorn app.main:app --reload    # or run start.bat on Windows
```

### Sample data

`backend/scripts/` has helpers for populating a development database (`seed_database.py`, `generate_sample_data.py`, `import_csv.py`). Example pressure recordings are in `backend/database/sample_data/`.

## Configuration

Settings are read from environment variables (see `backend/app/config.py`).

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL connection string | local `graphene_trace` database |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key | insecure dev value |
| `CORS_ORIGINS` | Allowed frontend origins | `localhost:5173`, `localhost:3000` |
| `DEBUG` | Debug mode | `True` |

> **Change `SECRET_KEY` before deploying.** The default is for development only. Generate one with `openssl rand -hex 32`.

## API overview

All routes are under `/api`:

| Prefix | Description |
| --- | --- |
| `/auth` | Login and tokens |
| `/users` | User and patient management |
| `/frames` | Pressure frames |
| `/metrics` | Computed metrics |
| `/alerts` | Pressure alerts |
| `/comments` | Comments on alerts and frames |
| `/movements` | Movement events |
| `/risk` | Risk scores |
| `/posture` | Posture labels |

The full, interactive reference is at `/docs` when the API is running.

## Testing

```bash
# Backend
cd backend
pytest --cov=app

# Frontend
cd frontend
npm test
npm run lint
```

## Project structure

```text
backend/
  app/
    api/routes/     HTTP endpoints
    models/         SQLAlchemy models
    schemas/        Pydantic schemas
    services/       auth, authorization, risk and movement analysis
    workers/        background metrics processing
    utils/          pressure-matrix and region helpers
  alembic/          database migrations
  scripts/          seed and data-import helpers
  tests/            pytest suite
frontend/
  src/components/   alerts, auth, comments, heatmap, metrics, ml
```

## Deployment

- **API:** Fly.io, configured in `backend/fly.toml`
- **Frontend:** Netlify, configured in `frontend/netlify.toml`
- **CI:** `.github/workflows/ci.yml` lints, tests and builds both halves
