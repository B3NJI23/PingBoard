from datetime import datetime, timezone

from app import db

def make_result(name, up):
    return {
        "name": name, "type": "http", "address": "https://example.com", "up": up,
        "status_code": 200 if up else 500, "response_ms": 100 if up else None,
    }

def test_uptime_percent(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    now = datetime.now(timezone.utc).isoformat()

    db.save_results(now, [make_result("A", True)])
    db.save_results(now, [make_result("A", False)])

    [row] = db.get_uptime(24)
    assert row["name"] == "A"
    assert row["total_checks"] == 2
    assert row["uptime_percent"] == 50.0