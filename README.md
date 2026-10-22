# Quiz Assessment Platform

A FastAPI and PostgreSQL backend for a quiz assessment platform. The frontend can remain a separate HTML, CSS, and vanilla JavaScript application and call this API over HTTP.

## Phase 1 status

This repository now contains the backend foundation only: configuration, the PostgreSQL connection/session layer, a CORS-enabled FastAPI application, and a health endpoint. Authentication, database models, migrations, quiz APIs, attempts, and results are reserved for following phases.

## Technology stack

- Python 3.11+
- FastAPI and Uvicorn
- PostgreSQL with SQLAlchemy and Psycopg 3
- Pydantic Settings for environment configuration
- Pytest and HTTPX for upcoming automated tests
- Alembic for upcoming database migrations

## Project structure

```text
backend/
  main.py          # FastAPI application and health endpoint
  config.py        # Environment-based settings
  database.py      # SQLAlchemy engine and request session dependency
  routes/          # Future API route modules
  services/        # Future business-logic modules
  tests/           # Future automated tests
requirements.txt
.env.example
```

## Prerequisites

- Python 3.11 or newer
- PostgreSQL 15 or newer, running locally

## PostgreSQL setup (Windows PowerShell)

Create a local database and application user in `psql`:

```powershell
psql -U postgres
CREATE USER quiz_user WITH PASSWORD 'choose-a-strong-local-password';
CREATE DATABASE quiz_platform OWNER quiz_user;
\q
```

## Install and configure

From the repository root, create and activate a virtual environment, then install dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and replace `DATABASE_URL` with your PostgreSQL credentials and `SECRET_KEY` with a unique secret of at least 32 characters. The `.env` file is ignored by Git and must never be committed.

## Run and verify

Start the API:

```powershell
uvicorn backend.main:app --reload
```

In another PowerShell window, verify the database connection:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Expected response after PostgreSQL is configured:

```json
{"status":"ok","database":"connected"}
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Frontend connection

During local development, the backend accepts requests from `http://localhost:5500` and `http://127.0.0.1:5500`. Change `CORS_ORIGINS` in `.env` to the actual frontend development URL before starting the server. Production deployments should allow only their exact frontend origin.

## Tests

Automated endpoint tests will be added with the subsequent feature phases. Once present, run them with:

```powershell
pytest backend/tests
```
