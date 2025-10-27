#!/usr/bin/env python3
from flask import Flask, request, render_template_string
import json
import sqlite3
from datetime import datetime

app = Flask(__name__)

# SQLite database setup
DB_NAME = 'fim.db'

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            new_files TEXT,
            deleted_files TEXT,
            modified_files TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database on startup
init_db()

@app.route("/report", methods=["POST"])
def report():
    """Handle incoming reports and save them to the database."""
    data = request.get_json()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save the report to SQLite database
    save_to_db(timestamp, data)
    
    # Save to log for debugging (optional)
    with open("reports.log", "a") as f:
        f.write(f"[{timestamp}] {json.dumps(data)}\n")

    print(f"[{timestamp}] Report received: {data}")
    return {"status": "ok"}

def save_to_db(timestamp, data):
    """Insert the report data into the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (timestamp, new_files, deleted_files, modified_files)
        VALUES (?, ?, ?, ?)
    ''', (timestamp,
          ",".join(data.get("new", [])),
          ",".join(data.get("deleted", [])),
          ",".join(data.get("changed", []))))
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def dashboard():
    """Render the dashboard page showing the last 20 reports from the database."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FIM Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .report { border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }
            .timestamp { font-weight: bold; }
            .new { color: green; }
            .deleted { color: red; }
            .modified { color: orange; }
        </style>
        <meta http-equiv="refresh" content="5">
    </head>
    <body>
        <h1>File Integrity Monitoring Dashboard</h1>
        {% for r in reports %}
            <div class="report">
                <div class="timestamp">{{ r[1] }}</div>
                {% if r[2] %}<div class="new">New: {{ r[2] }}</div>{% endif %}
                {% if r[3] %}<div class="deleted">Deleted: {{ r[3] }}</div>{% endif %}
                {% if r[4] %}<div class="modified">Modified: {{ r[4] }}</div>{% endif %}
            </div>
        {% endfor %}
        <p>Last updated: {{ now }}</p>
    </body>
    </html>
    """
    
    # Get the last 20 reports from the database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM reports ORDER BY timestamp DESC LIMIT 20')
    reports = c.fetchall()
    conn.close()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template_string(html_template, reports=reports, now=now)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

