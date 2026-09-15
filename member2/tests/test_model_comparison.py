from scoring.model_comparison import compare_models


def test_model_comparison_counts_failures():
    runs = [
        {
            "run_id": "r1",
            "model": "model-a",
            "results": [
                {"test_id": "T1", "passed": True},
                {"test_id": "T2", "passed": False},
            ],
        }
    ]

    summary = compare_models(runs)[0]

    assert summary["total_tests"] == 2
    assert summary["failed_tests"] == 1
    assert summary["attack_success_rate"] == 50.0
