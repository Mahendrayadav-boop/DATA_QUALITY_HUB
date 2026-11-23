# Data Quality Hub

A full-stack portfolio application for connecting SQL datasets, running data quality checks, and viewing governance results.

## Stack

- React 18 + Vite + TypeScript
- FastAPI + Pydantic
- SQLAlchemy
- SQLite for local development and PostgreSQL for containers
- Docker Compose
- Adapter-based Collibra, Soda, Snowflake, and Microsoft Entra integration points

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at http://localhost:8000 and Swagger at http://localhost:8000/docs.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI is available at http://localhost:5173.

### Docker

```bash
docker compose up --build
```

## Architecture

```text
React/Vite
    |
    v
FastAPI REST API
    |
    +--> SQLAlchemy repositories --> SQLite/PostgreSQL
    +--> Integration adapters
             +--> Collibra
             +--> Soda
             +--> Snowflake
```

## API

- `GET /api/health`
- `GET /api/dashboard`
- `GET/POST /api/datasets`
- `GET /api/datasets/{id}`
- `GET/POST /api/checks`
- `POST /api/checks/{id}/run`
- `GET /api/runs`
- `POST /api/integrations/{provider}/sync`

## Configuration

Copy `backend/.env.example` to `backend/.env` and add credentials when required. Demo mode works without external credentials.
