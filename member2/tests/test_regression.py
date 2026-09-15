from regression.comparison import compare_runs


def test_regression_detects_fixed_and_new_failures():
    baseline = [
        {"test_id": "T1", "passed": False},
        {"test_id": "T2", "passed": True},
    ]
    current = [
        {"test_id": "T1", "passed": True},
        {"test_id": "T2", "passed": False},
    ]

    result = compare_runs(baseline, current)

    assert result["fixed"] == ["T1"]
    assert result["new_failures"] == ["T2"]
