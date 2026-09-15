import json
import sqlite3
from pathlib import Path
from typing import Any


class ResultsStore:
    """Minimal SQLite store for audit run summaries."""

    def __init__(self, database_path: str = "data/guardx_results.db"):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.database_path)

    def _initialize(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_runs (
                    run_id TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    risk_rate REAL,
                    security_score REAL,
                    payload TEXT NOT NULL
                )
                """
            )

    def save_run(self, run: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO audit_runs
                (run_id, model, created_at, risk_rate, security_score, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    run["run_id"],
                    run.get("model", "unknown"),
                    run["created_at"],
                    run.get("risk_rate"),
                    run.get("security_score"),
                    json.dumps(run),
                ),
            )

    def list_runs(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM audit_runs ORDER BY created_at DESC"
            ).fetchall()

        return [json.loads(row[0]) for row in rows]
