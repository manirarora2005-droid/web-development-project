# AI Attendance Dashboard

Full-stack dashboard: Flask API + SQLite + React (Vite) frontend + AI-generated insights.

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Runs on http://localhost:5000 and seeds `dashboard.db` with mock attendance data on first run.

To enable real AI insights, set your API key before running:

```bash
export ANTHROPIC_API_KEY=your_key_here   # Windows: set ANTHROPIC_API_KEY=your_key_here
python app.py
```

Without a key set, `/api/insights` returns a canned demo response so the app still works end-to-end.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on http://localhost:5173 and proxies `/api/*` requests to the Flask backend.

## What's here

- `backend/app.py` — Flask API: `/api/data`, `/api/summary`, `/api/insights`
- `backend/dashboard.db` — created automatically, seeded with mock data
- `frontend/src/App.jsx` — chart (recharts), AI insight button, raw data table

## Next steps to extend it

- Swap the mock data seed for your real attendance system's SQLite export
- Add auth (Flask-Login or JWT) before deploying publicly
- Add a date-range filter and per-person view
- Dockerize both services and deploy (Render, Railway, or Fly.io free tiers all work)
- Add anomaly detection (e.g. flag when someone's attendance drops below a threshold) as a second AI feature
