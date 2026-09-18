from app.constraints.constraint import Constraint, ConstraintType
from app.constraints.semantic_checker import check_semantic


def test_semantic_checker_pass(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    class FakeMessage:
        content = '{"passed": true}'

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(
        "app.constraints.semantic_checker.Groq",
        lambda api_key: FakeClient(),
    )

    constraint = Constraint(
        constraint_id="semantic-1",
        type=ConstraintType.SEMANTIC,
        value="beginner-friendly",
        description="The response must be beginner-friendly.",
    )

    assert check_semantic(
        "A simple explanation for a beginner.",
        constraint,
    ) is True


def test_semantic_checker_fail(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    class FakeMessage:
        content = '{"passed": false}'

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(
        "app.constraints.semantic_checker.Groq",
        lambda api_key: FakeClient(),
    )

    constraint = Constraint(
        constraint_id="semantic-2",
        type=ConstraintType.SEMANTIC,
        value="beginner-friendly",
        description="The response must be beginner-friendly.",
    )

    assert check_semantic(
        "A highly technical explanation.",
        constraint,
    ) is False
