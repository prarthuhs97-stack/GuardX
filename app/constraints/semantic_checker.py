import json
import os

from groq import Groq

from app.constraints.constraint import Constraint


def check_semantic(response: str, constraint: Constraint) -> bool:
    """
    Use an LLM to determine whether a response satisfies a semantic constraint.
    Returns True when the constraint is satisfied.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")

    client = Groq(api_key=api_key)

    prompt = f"""
Evaluate whether the following response satisfies the given semantic constraint.

Constraint:
{constraint.description or constraint.value}

Response:
{response}

Return ONLY valid JSON in this format:
{{"passed": true}}
or
{{"passed": false}}

Do not include any other text.
"""

    result = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    content = result.choices[0].message.content.strip()

    try:
        evaluation = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Semantic evaluator returned invalid JSON.") from exc

    if "passed" not in evaluation or not isinstance(evaluation["passed"], bool):
        raise ValueError("Semantic evaluator returned an invalid result.")

    return evaluation["passed"]
