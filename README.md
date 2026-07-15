# TrekScape

TrekScape is a Flask + Vue 3 trekking management app with SQLite, JWT auth, Redis caching, and Celery background jobs.

## Project Structure

- `backend/` Flask application, routes, services, models, Celery, and config
- `frontend/` Vue 3 application
- `tests/` backend test suite

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- Redis 6+ running locally

## Environment Setup

1. Copy `backend/.env.example` to `backend/.env`.
2. Update the values if needed. The safe local defaults are:


## Install Dependencies

Backend:

```bash
python -m pip install -r backend/requirements.txt
```

Frontend:

```bash
cd frontend
npm install
```

## Start Redis

Run Redis before starting the backend or Celery workers.

If you are using WSL / Ubuntu:

```bash
wsl -d Ubuntu
sudo service redis-server start
redis-cli ping
```

If Redis is installed locally on Windows, start it using your local Redis service or process manager and confirm with `redis-cli ping`.

## Start the Backend

From the repository root:

```bash
python -m backend.create_admin
python -m backend.app
```


## Start Celery Worker

Open a second terminal from the repository root:

```bash
python -m celery -A backend.celery_worker:celery worker --pool=solo --loglevel=info
```

## Start Celery Beat

Open a third terminal from the repository root:

```bash
python -m celery -A backend.celery_worker:celery beat --loglevel=info
```

## Start the Frontend

Open a fourth terminal:

```bash
cd frontend
npm run dev
```

## Optional Manual Job Smoke Test

You can manually queue the scheduled jobs during development:

```bash
python -m backend.manual_scheduled_jobs_smoke daily
python -m backend.manual_scheduled_jobs_smoke monthly
```

## Suggested Startup Order

1. Start Redis.
2. Start the Flask backend.
3. Start the Celery worker.
4. Start Celery Beat.
5. Start the Vue frontend.

## Notes

- The backend API is the source of truth; Redis is used for Celery and API caching only.
- The frontend expects the backend to be available on the default API base used by the existing axios client.
- If you change environment variables, restart the backend, Celery worker, and Celery Beat so they pick up the new settings.


