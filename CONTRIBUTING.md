# Contributing to prompt-lab

Welcome. This repo is a **day-5 teaching A/B prompt eval harness** — two prompts, fixed cases, pure scorers, declare a winner. Keep that bar in mind.

## Map (fork → PR)

1. **Fork** this repo on GitHub, then clone your fork:
   ```bash
   git clone https://github.com/<you>/prompt-lab.git
   cd prompt-lab
   ```
2. **Install** in editable mode with test deps:
   ```bash
   pip install -e ".[dev]"
   ```
3. **Prove the wiring** before you change anything:
   ```bash
   pytest
   python -m prompt_lab --mock
   ```
   You want `16 passed` and a table where **B** wins by 15.0 pts. No API key needed.
4. **Branch** for one small change:
   ```bash
   git checkout -b my-first-pr
   ```
5. **Ship** a focused PR back to `primeodin/prompt-lab`:
   - one idea per PR
   - include or update a test when behavior changes
   - say what you ran (`pytest`, `python -m prompt_lab --mock`)

## Add a scorer or case

1. Implement a pure function in `src/prompt_lab/scorers.py` (no I/O, no randomness).
2. Or add an `EvalCase` in `src/prompt_lab/cases.py` with a stable `expected` label.
3. Extend `MockModel` only if the new case needs a new keyword rule.
4. Add a test under `tests/` that fails without your change and passes with it.
5. Update the README table / expected stdout if totals change.

Keep scorers deterministic. The mock is sacred — offline tests must keep working without secrets.

## Good first issues

Scoped tickets (file named in the issue body):

- [#1 — `starts_with_label` scorer + rubric weight](https://github.com/primeodin/prompt-lab/issues/1)
- [#2 — `--csv` export of the comparison table](https://github.com/primeodin/prompt-lab/issues/2)
- [#3 — Extra summarize case pack selectable via flag](https://github.com/primeodin/prompt-lab/issues/3)

Claim one with a comment, ask questions in the thread, then open the PR. Docs count.

## Shop rules

- **Keep it small.** No LangChain / eval-framework pile-ons, no extra services "while we're here."
- **Mock stays sacred.** Offline tests and `--mock` must keep working without secrets.
- **Scorers are pure.** If a scorer lies, the winner is a lie — fix the scorer, don't yell at the model.
- **Teach by running.** Prefer a mock path + a test over a theory dump.
- **Match the voice.** Short, concrete, honest — shop notes, not pitch decks.

## What to skip

Please don't open PRs that:

- add a heavy eval/framework stack
- require paid APIs in the default path
- rewrite the README for marketing tone
- bundle unrelated refactors with a feature

Questions? Comment on the issue you're claiming — that thread is the right place.
