# TrekScape

Minimal MVC scaffold for the Trekking Management Application.

## Structure

- backend/ for Flask application, routes, services, and configuration
- frontend/ for Vue 3 application structure

## Getting Started

### 1. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.\.venv\Scripts\activate    # Windows PowerShell
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
python app.py
```

The backend should start on http://localhost:5000.

### 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The frontend should start on http://localhost:5173.


## Notes

- The backend authentication APIs are already wired for registration and login.
- The frontend uses JWT-based authentication with protected routes.
- No dashboard implementation is required for this verification step; placeholder protected pages are enough.
