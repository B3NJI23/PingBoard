import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "pingboard.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
                        CREATE TABLE IF NOT EXISTS checks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        checked_at TEXT NOT NULL,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        address TEXT NOT NULL,
                        up INTEGER NOT NULL,
                        status_code INTEGER,
                        response_ms INTEGER,
                        error TEXT
                        
                        )
                    """)

def save_results(checked_at : str, results : list[dict]) -> None:
    rows = [
        (checked_at, r["name"], r["type"], r["address"], int(r["up"]), 
         r["status_code"], r["response_ms"], r.get("error"))
         for r in results
    ]

    with get_connection() as conn:
        conn.executemany(
            """INSERT INTO checks
            (checked_at, name, type, address, up, status_code, response_ms, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            rows
        )

def get_uptime(hours : int = 24) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT name,
                COUNT(*) AS total_checks,
                SUM(up) AS up_checks,
                ROUND(100.0 * SUM(up) / COUNT(*), 2) AS uptime_percent,
                ROUND(AVG(response_ms)) AS avg_response_ms
            FROM checks
            WHERE checked_at >= ?
            GROUP BY name
            ORDER BY name
""", (since,)).fetchall()

    return [dict(row) for row in rows]
