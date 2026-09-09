"""Pure deterministic scorers — no LLM-as-judge here."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    name: str
    points: float
    detail: str = ""


Scorer = Callable[[str, str], Score]


def exact_match(output: str, expected: str) -> Score:
    got = output.strip().lower()
    want = expected.strip().lower()
    hit = got == want
    return Score(
        name="exact_match",
        points=1.0 if hit else 0.0,
        detail=f"got={got!r} want={want!r}",
    )


def contains_keyword(output: str, keyword: str) -> Score:
    hit = keyword.lower() in output.lower()
    return Score(
        name="contains_keyword",
        points=1.0 if hit else 0.0,
        detail=f"keyword={keyword!r}",
    )


def length_band(output: str, lo: int, hi: int) -> Score:
    n = len(output.strip())
    hit = lo <= n <= hi
    return Score(
        name="length_band",
        points=1.0 if hit else 0.0,
        detail=f"len={n} band=[{lo},{hi}]",
    )


def rubric_points(output: str, expected: str, keyword: str) -> Score:
    """Shop rubric: exact label (2) + keyword present (1) + short reply (1)."""
    pts = 0.0
    bits: list[str] = []
    em = exact_match(output, expected)
    pts += 2.0 * em.points
    bits.append(f"exact={em.points}")
    ck = contains_keyword(output, keyword)
    pts += ck.points
    bits.append(f"kw={ck.points}")
    # Prefer one-word labels; soft-fail long waffle.
    lb = length_band(output, 1, 24)
    pts += lb.points
    bits.append(f"len={lb.points}")
    return Score(name="rubric_points", points=pts, detail="; ".join(bits))
