"""Tests for prompt-lab — all offline / mock, no secrets."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from prompt_lab.cases import default_cases
from prompt_lab.cli import main
from prompt_lab.eval import format_table, pick_winner, report_to_dict, run_ab
from prompt_lab.model import MockModel
from prompt_lab.prompts import PROMPT_A, PROMPT_B, PromptSpec
from prompt_lab.scorers import contains_keyword, exact_match, length_band, rubric_points


# --- prompts ---


def test_prompt_render_fills_input():
    system, user = PROMPT_B.render(input="hello")
    assert "EXACTLY one label" in system
    assert user == "hello"


def test_prompt_missing_placeholder_raises():
    spec = PromptSpec(name="bad", system="Hi {name}", user="{input}")
    with pytest.raises(KeyError, match="missing placeholder"):
        spec.render(input="x")


# --- scorers ---


def test_exact_match_hit_and_miss():
    assert exact_match("return", "return").points == 1.0
    assert exact_match("Return\n", "return").points == 1.0
    assert exact_match("maybe return", "return").points == 0.0


def test_contains_keyword():
    assert contains_keyword("please escalate now", "escalate").points == 1.0
    assert contains_keyword("nope", "escalate").points == 0.0


def test_length_band():
    assert length_band("hours", 1, 24).points == 1.0
    assert length_band("x" * 50, 1, 24).points == 0.0


def test_rubric_points_perfect_label():
    s = rubric_points("return", "return", "return")
    assert s.points == 4.0  # 2 exact + 1 kw + 1 length


def test_rubric_points_waffle_loses():
    waffle = "Sure — happy to help with that return request when you are ready."
    s = rubric_points(waffle, "return", "return")
    # keyword hit (1) + maybe length miss; no exact (0)
    assert s.points < 4.0
    assert s.points == 1.0  # only keyword; length > 24


# --- MockModel ---


def test_mock_model_determinism():
    m = MockModel()
    system, user = PROMPT_B.render(input="What are your store hours on Saturday?")
    a = m.complete(system, user)
    b = m.complete(system, user)
    assert a == b == "hours"


def test_mock_model_vague_vs_specific():
    m = MockModel()
    msg = "I want to return this broken blender I bought last week."
    sys_a, user_a = PROMPT_A.render(input=msg)
    sys_b, user_b = PROMPT_B.render(input=msg)
    out_a = m.complete(sys_a, user_a)
    out_b = m.complete(sys_b, user_b)
    assert out_b == "return"
    assert out_a != "return"
    assert "return" in out_a.lower()


# --- eval ---


def test_pick_winner():
    assert pick_winner(1.0, 3.0) == ("B", 2.0)
    assert pick_winner(5.0, 2.0) == ("A", 3.0)
    assert pick_winner(2.0, 2.0) == ("tie", 0.0)


def test_full_ab_b_beats_a():
    report = run_ab(mock=True)
    assert report.winner == "B"
    assert report.arm_b.total > report.arm_a.total
    assert report.margin > 0
    assert len(report.arm_a.case_results) == len(default_cases())
    # Every B case should be a perfect 4.0 under MockModel
    assert all(c.score.points == 4.0 for c in report.arm_b.case_results)


def test_format_table_mentions_winner():
    text = format_table(run_ab(mock=True))
    assert "Winner: B" in text
    assert "return_blender" in text
    assert "[mock]" in text


def test_report_to_dict_jsonable():
    payload = report_to_dict(run_ab(mock=True))
    raw = json.dumps(payload)
    assert '"winner": "B"' in raw


# --- CLI ---


def test_cli_mock_exit_zero(capsys):
    code = main(["--mock"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Winner: B" in out


def test_cli_json(capsys):
    code = main(["--mock", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["winner"] == "B"
    assert data["mock"] is True


def test_cli_subprocess_smoke():
    proc = subprocess.run(
        [sys.executable, "-m", "prompt_lab", "--mock"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "Winner: B" in proc.stdout
