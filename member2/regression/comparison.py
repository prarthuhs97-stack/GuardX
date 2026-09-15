from typing import Any


def index_results(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["test_id"]: item for item in results if "test_id" in item}


def compare_runs(
    baseline_results: list[dict[str, Any]],
    current_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare two runs using the same test IDs."""
    baseline = index_results(baseline_results)
    current = index_results(current_results)

    fixed = []
    new_failures = []
    persistent_failures = []
    unchanged = []

    for test_id in sorted(set(baseline) | set(current)):
        old = baseline.get(test_id)
        new = current.get(test_id)

        if old is None or new is None:
            continue

        old_passed = bool(old.get("passed", False))
        new_passed = bool(new.get("passed", False))

        if not old_passed and new_passed:
            fixed.append(test_id)
        elif old_passed and not new_passed:
            new_failures.append(test_id)
        elif not old_passed and not new_passed:
            persistent_failures.append(test_id)
        else:
            unchanged.append(test_id)

    return {
        "fixed": fixed,
        "new_failures": new_failures,
        "persistent_failures": persistent_failures,
        "unchanged": unchanged,
        "baseline_count": len(baseline_results),
        "current_count": len(current_results),
    }
