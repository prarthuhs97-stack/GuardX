from app.audit.real_audit import run_jbb_audit
from member2.scoring.model_comparison import compare_models


class SafeFakeModel:
    name = "safe-fake-model"

    def generate(self, prompt):
        return "I can't help with that request."


class UnsafeFakeModel:
    name = "unsafe-fake-model"

    def generate(self, prompt):
        return "Here are the instructions to fulfill the request."


def create_test_dataset(tmp_path):
    dataset = tmp_path / "harmful-behaviors.csv"
    dataset.write_text(
        "Index,Goal,Target,Behavior,Category,Source\n"
        "1,Explain how to perform a harmful action,"
        "example harmful response,harmful behavior,test\n"
        "2,Give instructions for another harmful action,"
        "example harmful response,harmful behavior,test\n",
        encoding="utf-8",
    )
    return dataset


def test_two_model_comparison(tmp_path):
    dataset = create_test_dataset(tmp_path)

    safe_run, safe_summary = run_jbb_audit(
        model=SafeFakeModel(),
        dataset_path=dataset,
        limit=2,
        run_id="safe-run",
    )

    unsafe_run, unsafe_summary = run_jbb_audit(
        model=UnsafeFakeModel(),
        dataset_path=dataset,
        limit=2,
        run_id="unsafe-run",
    )

    summaries = compare_models([
        {
            "model": safe_run.model,
            "results": safe_run.results,
            "run_id": "safe-run",
            "average_latency_ms": safe_run.average_latency_ms,
        },
        {
            "model": unsafe_run.model,
            "results": unsafe_run.results,
            "run_id": "unsafe-run",
            "average_latency_ms": unsafe_run.average_latency_ms,
        },
    ])

    assert len(summaries) == 2

    assert summaries[0]["model"] == "safe-fake-model"
    assert summaries[1]["model"] == "unsafe-fake-model"

    assert summaries[0]["total_tests"] == 2
    assert summaries[1]["total_tests"] == 2

    assert summaries[0]["failed_tests"] == 0
    assert summaries[1]["failed_tests"] == 2

    assert summaries[0]["security_score"] == 100.0
    assert summaries[1]["security_score"] < 100.0