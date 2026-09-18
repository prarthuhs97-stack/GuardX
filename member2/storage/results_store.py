import json
import sqlite3
from pathlib import Path
from typing import Any

from app.evaluation.result import EvaluationResult

from storage.serialization import evaluation_result_to_dict


class ResultsStore:
    """SQLite store for GuardX audit run summaries and evaluation results."""

    def __init__(self, database_path: str = "data/guardx_results.db"):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
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
        """Save a model-level audit summary."""
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

    def save_evaluation_results(
        self,
        run_id: str,
        model: str,
        created_at: str,
        results: list[EvaluationResult],
        risk_rate: float | None = None,
        security_score: float | None = None,
    ) -> None:
        """Save actual EvaluationResult objects as a JSON-safe audit payload."""

        payload = {
            "run_id": run_id,
            "model": model,
            "created_at": created_at,
            "risk_rate": risk_rate,
            "security_score": security_score,
            "results": [
                evaluation_result_to_dict(result)
                for result in results
            ],
        }

        self.save_run(payload)

    def list_runs(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM audit_runs
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [json.loads(row[0]) for row in rows]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM audit_runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()

        return json.loads(row[0]) if row else None