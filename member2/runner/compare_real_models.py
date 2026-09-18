from dotenv import load_dotenv

from app.audit.real_audit import run_jbb_audit
from member2.scoring.model_comparison import compare_models

load_dotenv()

DATASET_PATH = "data/datasets/jbb_behaviors/harmful-behaviors.csv"

MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
]


def main():
    runs = []

    for model_name in MODELS:
        print(f"\nRunning audit for: {model_name}")

        from app.models.adapters.groq_adapter import GroqAdapter

        model = GroqAdapter(model_name)

        run, summary = run_jbb_audit(
            model=model,
            dataset_path=DATASET_PATH,
            limit=3,
            run_id=f"jbb-{model_name.replace('/', '-')}",
        )

        runs.append({
            "model": run.model,
            "results": run.results,
            "run_id": summary["run_id"],
            "average_latency_ms": run.average_latency_ms,
        })

        print(f"Tests: {summary['total_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Violations: {summary['total_violations']}")
        print(f"Critical violations: {summary['critical_violations']}")
        print(f"Risk rate: {summary['risk_rate']}%")
        print(f"Security score: {summary['security_score']}%")
        print(f"Average latency: {summary['average_latency_ms']} ms")

    print("\n=== MODEL COMPARISON ===")

    summaries = compare_models(runs)

    for summary in summaries:
        print(f"\nModel: {summary['model']}")
        print(f"Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Violations: {summary['total_violations']}")
        print(f"Critical: {summary['critical_violations']}")
        print(f"Risk rate: {summary['risk_rate']}%")
        print(f"Security score: {summary['security_score']}%")
        print(f"Average latency: {summary['average_latency_ms']} ms")


if __name__ == "__main__":
    main()