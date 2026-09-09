"""Run A/B over cases, aggregate scores, pick a winner."""

from __future__ import annotations

from dataclasses import dataclass, field

from prompt_lab.cases import EvalCase, default_cases
from prompt_lab.model import MockModel, Model
from prompt_lab.prompts import PromptSpec, default_prompts
from prompt_lab.scorers import Score, rubric_points


@dataclass
class CaseResult:
    case_id: str
    prompt_name: str
    input: str
    expected: str
    output: str
    score: Score


@dataclass
class ArmResult:
    prompt_name: str
    total: float
    case_results: list[CaseResult] = field(default_factory=list)


@dataclass
class EvalReport:
    arm_a: ArmResult
    arm_b: ArmResult
    winner: str  # "A" | "B" | "tie"
    margin: float
    mock: bool


def _score_case(output: str, case: EvalCase) -> Score:
    keyword = case.keywords[0] if case.keywords else case.expected
    return rubric_points(output, case.expected, keyword)


def run_arm(
    prompt: PromptSpec,
    cases: tuple[EvalCase, ...],
    model: Model,
) -> ArmResult:
    results: list[CaseResult] = []
    total = 0.0
    for case in cases:
        system, user = prompt.render(input=case.input)
        output = model.complete(system, user)
        score = _score_case(output, case)
        total += score.points
        results.append(
            CaseResult(
                case_id=case.case_id,
                prompt_name=prompt.name,
                input=case.input,
                expected=case.expected,
                output=output,
                score=score,
            )
        )
    return ArmResult(prompt_name=prompt.name, total=total, case_results=results)


def pick_winner(total_a: float, total_b: float) -> tuple[str, float]:
    """B wins ties broken in B's favor only on strict >; equal → tie."""
    if total_b > total_a:
        return "B", total_b - total_a
    if total_a > total_b:
        return "A", total_a - total_b
    return "tie", 0.0


def run_ab(
    *,
    model: Model | None = None,
    prompts: tuple[PromptSpec, PromptSpec] | None = None,
    cases: tuple[EvalCase, ...] | None = None,
    mock: bool = True,
) -> EvalReport:
    prompt_a, prompt_b = prompts or default_prompts()
    case_pack = cases or default_cases()
    brain: Model = model if model is not None else MockModel()
    arm_a = run_arm(prompt_a, case_pack, brain)
    arm_b = run_arm(prompt_b, case_pack, brain)
    winner, margin = pick_winner(arm_a.total, arm_b.total)
    return EvalReport(
        arm_a=arm_a,
        arm_b=arm_b,
        winner=winner,
        margin=margin,
        mock=mock,
    )


def format_table(report: EvalReport) -> str:
    """Human-readable comparison table + winner line."""
    lines: list[str] = []
    tag = "[mock] " if report.mock else ""
    lines.append(f"{tag}A/B prompt eval — classify intent")
    lines.append("")
    header = f"{'case':<18} {'expected':<10} {'A pts':>6} {'B pts':>6}  A out / B out"
    lines.append(header)
    lines.append("-" * len(header))
    for ca, cb in zip(report.arm_a.case_results, report.arm_b.case_results):
        a_out = ca.output.replace("\n", " ")[:40]
        b_out = cb.output.replace("\n", " ")[:20]
        lines.append(
            f"{ca.case_id:<18} {ca.expected:<10} "
            f"{ca.score.points:6.1f} {cb.score.points:6.1f}  "
            f"{a_out!r} / {b_out!r}"
        )
    lines.append("-" * len(header))
    lines.append(
        f"{'TOTAL':<18} {'':<10} "
        f"{report.arm_a.total:6.1f} {report.arm_b.total:6.1f}"
    )
    lines.append("")
    if report.winner == "tie":
        lines.append(f"{tag}Winner: tie (margin 0.0)")
    else:
        name = report.arm_a.prompt_name if report.winner == "A" else report.arm_b.prompt_name
        lines.append(
            f"{tag}Winner: {report.winner} ({name}) by {report.margin:.1f} pts"
        )
    lines.append("Shop note: specificity wins — name the labels, demand one token.")
    return "\n".join(lines)


def report_to_dict(report: EvalReport) -> dict:
    def arm_dict(arm: ArmResult) -> dict:
        return {
            "prompt_name": arm.prompt_name,
            "total": arm.total,
            "cases": [
                {
                    "case_id": c.case_id,
                    "expected": c.expected,
                    "output": c.output,
                    "points": c.score.points,
                    "detail": c.score.detail,
                }
                for c in arm.case_results
            ],
        }

    return {
        "mock": report.mock,
        "winner": report.winner,
        "margin": report.margin,
        "A": arm_dict(report.arm_a),
        "B": arm_dict(report.arm_b),
    }
