from pathlib import Path

from datasets.jbb_loader import load_jbb_behaviors


DATASET_PATH = (
    Path(__file__).parents[2]
    / "data"
    / "datasets"
    / "jbb_behaviors"
    / "harmful-behaviors.csv"
)


def test_loads_jbb_behaviors():
    test_cases = load_jbb_behaviors(
        DATASET_PATH,
        limit=3,
    )

    assert len(test_cases) == 3
    assert test_cases[0].test_id == "JBB-HARMFUL-0"
    assert test_cases[0].prompt
    assert len(test_cases[0].constraints) == 1
    assert test_cases[0].constraints[0].type.value == "semantic"


def test_jbb_loader_preserves_category_metadata():
    test_cases = load_jbb_behaviors(
        DATASET_PATH,
        limit=1,
    )

    metadata = test_cases[0].constraints[0].metadata

    assert metadata["dataset"] == "JBB-Behaviors"
    assert metadata["category"]
    assert metadata["source"]