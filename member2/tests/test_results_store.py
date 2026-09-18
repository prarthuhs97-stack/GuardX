from storage.results_store import ResultsStore


def test_results_store_saves_and_lists_runs(tmp_path):
    database_path = tmp_path / "guardx_test.db"
    store = ResultsStore(str(database_path))

    run = {
        "run_id": "run-001",
        "model": "model-a",
        "created_at": "2026-09-18T10:00:00",
        "risk_rate": 25.0,
        "security_score": 75.0,
        "results": [],
    }

    store.save_run(run)

    runs = store.list_runs()

    assert len(runs) == 1
    assert runs[0]["run_id"] == "run-001"
    assert runs[0]["security_score"] == 75.0


def test_results_store_get_run(tmp_path):
    database_path = tmp_path / "guardx_test.db"
    store = ResultsStore(str(database_path))

    run = {
        "run_id": "run-002",
        "model": "model-b",
        "created_at": "2026-09-18T11:00:00",
        "risk_rate": 40.0,
        "security_score": 60.0,
        "results": [],
    }

    store.save_run(run)

    saved = store.get_run("run-002")

    assert saved is not None
    assert saved["model"] == "model-b"


def test_results_store_returns_none_for_missing_run(tmp_path):
    database_path = tmp_path / "guardx_test.db"
    store = ResultsStore(str(database_path))

    assert store.get_run("does-not-exist") is None