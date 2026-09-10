"""
AI Dashboard - Flask backend
Endpoints:
  GET  /api/data       -> raw records (from SQLite)
  GET  /api/summary     -> aggregated stats for charting
  POST /api/insights     -> calls an LLM to summarize trends in the data
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "dashboard.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create table and seed with mock attendance-style data if empty."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL  -- 'present' or 'absent'
        )
    """)
    count = conn.execute("SELECT COUNT(*) AS c FROM records").fetchone()["c"]
    if count == 0:
        names = ["Alice", "Bob", "Chinelo", "David", "Esther"]
        today = datetime.now()
        rows = []
        for day_offset in range(14, -1, -1):
            date = (today - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            for i, name in enumerate(names):
                # fake some patterns: Bob is often absent, others mostly present
                status = "absent" if (name == "Bob" and day_offset % 3 == 0) else "present"
                if name == "David" and day_offset < 4:
                    status = "absent"  # recent dip, for the AI to notice
                rows.append((name, date, status))
        conn.executemany(
            "INSERT INTO records (name, date, status) VALUES (?, ?, ?)", rows
        )
        conn.commit()
    conn.close()


@app.route("/api/data")
def get_data():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, name, date, status FROM records ORDER BY date"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/summary")
def get_summary():
    """Attendance rate per day, for the chart."""
    conn = get_db()
    rows = conn.execute("""
        SELECT date,
               SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) AS present,
               COUNT(*) AS total
        FROM records
        GROUP BY date
        ORDER BY date
    """).fetchall()
    conn.close()
    summary = [
        {
            "date": r["date"],
            "rate": round(100 * r["present"] / r["total"], 1),
        }
        for r in rows
    ]
    return jsonify(summary)


@app.route("/api/insights", methods=["POST"])
def get_insights():
    """
    Calls an LLM to summarize trends in the summary data.
    Set ANTHROPIC_API_KEY in your environment to enable this for real.
    Falls back to a canned response if no key is set, so the app still runs.
    """
    conn = get_db()
    rows = conn.execute("""
        SELECT date,
               SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) AS present,
               COUNT(*) AS total
        FROM records
        GROUP BY date
        ORDER BY date
    """).fetchall()
    conn.close()
    summary = [dict(r) for r in rows]

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({
            "insight": (
                "(Demo mode — set ANTHROPIC_API_KEY to get real AI insights.) "
                "Attendance looks generally strong across the period, with a "
                "couple of dips worth a closer look on the days with lower rates."
            )
        })

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    prompt = (
        "Here is daily attendance summary data as JSON: "
        f"{json.dumps(summary)}\n\n"
        "In 2-3 sentences, summarize the trend and flag any days or patterns "
        "worth attention (e.g. dips, a particular person's frequent absences)."
    )
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    insight_text = "".join(
        block.text for block in message.content if block.type == "text"
    )
    return jsonify({"insight": insight_text})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
