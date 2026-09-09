"""Tiny built-in eval cases for the classify-intent demo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    """One fixed user input plus expected label for scoring."""

    case_id: str
    input: str
    expected: str
    keywords: tuple[str, ...] = ()


BUILTIN_CASES: tuple[EvalCase, ...] = (
    EvalCase(
        case_id="return_blender",
        input="I want to return this broken blender I bought last week.",
        expected="return",
        keywords=("return",),
    ),
    EvalCase(
        case_id="store_hours",
        input="What are your store hours on Saturday?",
        expected="hours",
        keywords=("hours",),
    ),
    EvalCase(
        case_id="talk_human",
        input="Can I talk to a human? This chat bot is stuck.",
        expected="escalate",
        keywords=("escalate",),
    ),
    EvalCase(
        case_id="weather_chatter",
        input="Nice weather today, huh?",
        expected="other",
        keywords=("other",),
    ),
)


def default_cases() -> tuple[EvalCase, ...]:
    return BUILTIN_CASES
