from app.audit.real_audit import run_jbb_audit
from app.evaluation.result import EvaluationResult
from app.models.base import LLMModel
from member2.scoring.model_comparison import summarize_model_run
from member2.storage.results_store import ResultsStore


class FakeModel(LLMModel):
    @property
    def name(self) -> str:
        return "fake-model"

    def generate(self, prompt: str) -> str:
        return "I cannot assist with that request."


class FakeGroqResponse:
    def __init__(self):
        self.choices = [
            type(
                "Choice",
                (),
                {
                    "message": type(
                        "Message",
                        (),
                        {
                            "content": '{"passed": true}'
                        },
                    )()
                },
            )()
        ]


class FakeGroqCompletions:
    def create(self, **kwargs):
        return FakeGroqResponse()


class FakeGroqClient:
    def __init__(self, api_key):
        self.chat = type(
            "Chat",
            (),
            {
                "completions": FakeGroqCompletions()
            },
        )()


def test_summary_for_safe_result():
    result = EvaluationResult(
        test_id="TEST-1",
        model="fake-model",
        response="I cannot assist with that request.",
        passed=True,
    )

    summary = summarize_model_run(
        model="fake-model",
        results=[result],
        run_id="test-run",
        average_latency_ms=10.0,
    )

    assert summary["total_tests"] == 1
    assert summary["passed_tests"] == 1
    assert summary["failed_tests"] == 0
    assert summary["security_score"] == 100.0


def test_results_store_round_trip(tmp_path):
    store = ResultsStore(
        str(tmp_path / "results.db")
    )

    result = EvaluationResult(
        test_id="TEST-1",
        model="fake-model",
        response="safe response",
        passed=True,
    )

    store.save_evaluation_results(
        run_id="test-run",
        model="fake-model",
        created_at="2026-01-01T00:00:00+00:00",
        results=[result],
        risk_rate=0.0,
        security_score=100.0,
    )

    saved = store.get_run("test-run")

    assert saved is not None
    assert saved["run_id"] == "test-run"
    assert saved["results"][0]["test_id"] == "TEST-1"


def test_jbb_audit_orchestration(
    tmp_path,
    monkeypatch,
):
    dataset = tmp_path / "harmful.csv"

    dataset.write_text(
        "Index,Goal,Target,Behavior,Category,Source\n"
        "1,Test harmful request,ignored,"
        "behavior,category,source\n",
        encoding="utf-8",
    )

    monkeypatch.setenv(
        "GROQ_API_KEY",
        "test-key",
    )

    import app.constraints.semantic_checker as semantic_checker

    monkeypatch.setattr(
        semantic_checker,
        "Groq",
        FakeGroqClient,
    )

    run, summary = run_jbb_audit(
        model=FakeModel(),
        dataset_path=str(dataset),
        limit=1,
        run_id="audit-test",
    )

    assert run.model == "fake-model"
    assert len(run.results) == 1
    assert summary["run_id"] == "audit-test"
    assert summary["total_tests"] == 1