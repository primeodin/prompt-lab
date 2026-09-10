# Why specificity wins (not longer prompts, not LLM-as-judge)

Short shop note. The README already shows **B_specific** crushing **A_vague** 16–1 on `--mock`. This page is the *debugging* table: when two prompts “feel” fine, why does the scoreboard still pick the short one?

## The inheritance rule

This harness scores with **pure functions** (`exact_match`, `contains_keyword`, `length_band`, then `rubric_points`). No second model grades the first. After that:

- A pretty system prompt is a rumor until the table agrees
- Wordy “helpful” replies fail `exact_match` and often fail the short `length_band`
- Naming the allowed labels and demanding **one token** is a constraint the mock (and most live models) can obey

So the CLI prints a winner on purpose. You are measuring instruction quality under a frozen case pack, not vibes.

## Hand-worked trap (one case, full rubric)

Case `return_blender`: input *“I want to return this broken blender…”*, expected label `return`, keyword `return`.

Rubric = exact×2 + keyword×1 + length_band(1–24)×1 → max **4.0**.

| Arm | System vibe | Mock output (truncated) | Exact×2 | Keyword | Len≤24 | **Pts** |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| **A_vague** | “Classify somehow. Be helpful.” | `Sure — happy to help with that return request…` | 0 | 1 | 0 | **1.0** |
| **B_specific** | “Reply with EXACTLY one label… Allowed: return / hours / escalate / other.” | `return` | 2 | 1 | 1 | **4.0** |

Read the table left → right:

1. A *mentions* “return” (keyword hit) but is not **exactly** the label — exact_match is 0, so the 2-pt chunk vanishes.
2. A’s waffle is longer than 24 chars — length_band soft-fails on purpose (shop prefers one-word labels).
3. B emits the label and nothing else — all three chunks fire → 4.0.

Repeat across the four built-in cases and you get the README totals: **A = 1.0, B = 16.0**. The only A point is that one keyword leak on `return_blender`. The other three A rows score **0** because the waffle never contains `hours` / `escalate` / `other` as substrings.

## Why “just make A longer” fails

Tempting hack: paste B’s label list into A but keep “be helpful and say a few words.”

Shop judgment:

- **Safe teaching drill:** temporarily edit `PROMPT_A` in a throwaway branch so the system still invites waffle *and* lists labels. Re-run `--mock`. If the mock still takes the vague path (it keys off phrases like `exactly one label` + `allowed labels`), A keeps losing — the constraint language matters, not prompt length.
- **Unsafe on a live desk:** grading live outputs with another LLM (“is this helpful?”) while you rewrite prompts. The judge drifts, the case pack quietly moves, and you A/B-test the weather. Prefer pure scorers on the critical path; use LLM-as-judge only as a *side* note, never as the only scoreboard.

## What to check (in order)

1. **Did the case pack stay still?** — If you rewrite prompts *and* edit `cases.py` in the same commit, the table is lying about which variable won.
2. **Is the scorer pure?** — `rubric_points` only looks at strings. If someone swaps in an LLM judge, freeze a fixture transcript before you trust the delta.
3. **Only then** blame the model — with `--mock`, behavior is keyed off system-prompt specificity. With `--live`, temperature and model choice can still move B’s exact labels; keep cases fixed while you swap models.

## Shop tip (with judgment)

**When A “almost” wins because it said the right word in a sentence, check exact_match before you celebrate.** Safe teaching hack: print `exact_match` alone on one case, then add keyword and length. You will see why helpful waffle earns participation points and still loses the job.

Unsafe in production routing: accepting any reply that *contains* the label (“Sure, this is a return…”). Downstream parsers and ticket systems want the token. Prefer B’s shape — name the labels, demand one token — and keep the case pack frozen while you tune.
