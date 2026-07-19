import sqlite3
import os

DB_NAME = "promptx_logs.db"

def init_db():
    """Initializes the SQLite database and creates the logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            raw_prompt TEXT,
            status TEXT,
            risk_score INTEGER,
            risk_classification TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_incident(raw_prompt, status, risk_score, risk_classification):
    """Saves a prompt evaluation incident straight to the local database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO security_logs (raw_prompt, status, risk_score, risk_classification)
        VALUES (?, ?, ?, ?)
    ''', (raw_prompt, status, risk_score, risk_classification))
    conn.commit()
    conn.close()


def get_recent_logs(limit=8):
    """Return the latest redacted scan records for the local dashboard."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, raw_prompt, status, risk_score, risk_classification
        FROM security_logs
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
