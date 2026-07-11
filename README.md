# TrekScape

Minimal MVC scaffold for the Trekking Management Application.

## Structure

- backend/ for Flask application, routes, services, and configuration
- frontend/ for Vue 3 application structure

## Getting Started

Terminal 1 — Ubuntu / WSL
wsl -d Ubuntu
sudo service redis-server start
redis-cli ping

Terminal 2 — Windows PowerShell
celery -A backend.celery_worker:celery worker --pool=solo --loglevel=info

Terminal 3 — Windows PowerShell
python -m backend.app

Terminal 4 — Windows PowerShell
cd frontend
npm run dev

