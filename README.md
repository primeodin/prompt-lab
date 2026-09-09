# prompt-lab

> Day-5 of PrimeOdin’s daily public builds — a tiny A/B prompt eval harness with no framework soup.

**Two prompts. Same cases. Score the outputs. Declare a winner.** That is the whole trick. Shop teaching: specificity wins.

## 60-second start

```bash
git clone https://github.com/primeodin/prompt-lab.git
cd prompt-lab
pip install -e ".[dev]"
pytest
python -m prompt_lab --mock
python -m prompt_lab --mock --json
```

**Expected stdout** (deterministic on `--mock` — yours should match):

```text
# pytest
................                                                         [100%]
16 passed

# mock A/B eval
[mock] A/B prompt eval — classify intent

case               expected    A pts  B pts  A out / B out
----------------------------------------------------------
return_blender     return        1.0    4.0  'Sure — happy to help with that return re' / 'return'
store_hours        hours         0.0    4.0  'I can look into store timing for you; wh' / 'hours'
talk_human         escalate      0.0    4.0  'Of course, I understand wanting a person' / 'escalate'
weather_chatter    other         0.0    4.0  'Thanks for the message! How else can I a' / 'other'
----------------------------------------------------------
TOTAL                            1.0   16.0

[mock] Winner: B (B_specific) by 15.0 pts
Shop note: specificity wins — name the labels, demand one token.
```

If totals drift or B no longer wins, the mock, cases, or scorers changed — open an issue before "fixing" the table by eye.

## Why A/B eval matters

A pretty prompt is a rumor. An A/B table on **fixed cases** is a measurement. You keep the inputs still, swap only the instructions, score with boring deterministic checks, and let the numbers pick the winner. That kills cargo-cult prompting faster than another blog post.

Three mysteries go away once you run this harness yourself:

- why "be helpful" loses to "reply with EXACTLY one label"
- why scorers must stay pure (no LLM-as-judge in the critical path)
- why a mock model is enough to teach the loop before you spend tokens

## The whole loop, in five lines

1. Fix a tiny case pack (inputs + expected labels).
2. Render prompt A and prompt B for each case (`{input}` in, messages out).
3. Run both through the same model (mock in tests; live optional).
4. Score each output with pure functions (exact / keyword / length / rubric).
5. Sum the points, print a table, declare A / B / tie.

## Built-in demo

| Arm | System vibe | What MockModel does |
| --- | --- | --- |
| **A_vague** | "Classify somehow. Be helpful." | Wordy waffle — fails exact_match |
| **B_specific** | "Reply with EXACTLY one label: return / hours / escalate / other." | Emits the short label |

Cases: return a blender, ask store hours, ask for a human, weather chatter → `other`.

## Change one thing

1. Add a case in `cases.py` and watch the table grow  
2. Add a scorer in `scorers.py` (e.g. `starts_with_label`) and wire it into the rubric  
3. Swap `--mock` for `--live` when you have an `OPENAI_API_KEY` (or point `OPENAI_BASE_URL` at Ollama)

## Real model (optional)

```bash
export OPENAI_API_KEY=sk-...
# optional: export OPENAI_BASE_URL=http://localhost:11434/v1
python -m prompt_lab --live
```

Tests and `--mock` never need a key.

## What you just built

| Piece | Job |
| --- | --- |
| `prompts.py` | `PromptSpec` A/B templates with `{input}` |
| `cases.py` | Four fixed classify-intent cases |
| `model.py` | Deterministic `MockModel` + thin `LiveModel` |
| `scorers.py` | `exact_match` / `contains_keyword` / `length_band` / `rubric_points` |
| `eval.py` | Run A/B, aggregate, pick winner, format table |
| `cli.py` | `--mock` / `--live` / `--json` |

## Help / good first issues

Scoped tickets live in [Issues](https://github.com/primeodin/prompt-lab/issues). Open contribution ideas:

- **#1** — Add a `starts_with_label` scorer + rubric weight  
- **#2** — `--csv` export of the comparison table  
- **#3** — Extra case pack (summarize-in-one-sentence) selectable via flag  

New to pull requests? Start at [first-commit-ai](https://github.com/primeodin/first-commit-ai), then come back.

## Daily builds series

Tiny, tested teaching repos — starter → mid. Ship one, read it, then climb:

| Lane | Repo | Why open it |
| --- | --- | --- |
| Starter chat | [first-commit-ai](https://github.com/primeodin/first-commit-ai) | Mock-first chat CLI + pytest |
| Starter RAG | [notes-rag](https://github.com/primeodin/notes-rag) | Retrieve, cite, answer over Markdown notes |
| Starter tokenizer | [tiny-bpe-tokenizer](https://github.com/primeodin/tiny-bpe-tokenizer) | Watch text become token IDs — train, encode, decode |
| Mid tool agent | [tiny-tool-agent](https://github.com/primeodin/tiny-tool-agent) | ReAct: Thought, Action, Observation, Final Answer |
| Mid prompt lab (this) | [prompt-lab](https://github.com/primeodin/prompt-lab) | A/B eval: two prompts, fixed cases, score, winner |
| Attention mid | [attention-warrior](https://github.com/primeodin/attention-warrior) | Transformer attention you can hold in one hand |
| Shop skills | [mister-jay](https://github.com/primeodin/mister-jay) | Interactive DIY drills — [live](https://primeodin.github.io/mister-jay/) |
| Literacy (Sinhala) | [jay-ai-sinhala](https://github.com/primeodin/jay-ai-sinhala) | Friends 70+ learning GitHub + AI — [live](https://primeodin.github.io/jay-ai-sinhala/) |
| Systems DIY | [camera-selector](https://github.com/primeodin/camera-selector) | NVR/Frigate camera planning — [live](https://primeodin.github.io/camera-selector/) |

Weekday cadence, in order: chat CLI → RAG → tokenizer → tool agent → **prompt lab (this)** → embedding playground → vision → memory → shop-skill explainer.

Profile forge: [github.com/primeodin](https://github.com/primeodin)

## License

MIT
