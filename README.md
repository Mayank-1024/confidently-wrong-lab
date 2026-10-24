# Confidently Wrong Lab

**When an LLM judge says it's sure, how often is it wrong, and which oversight catches it?**

Project 1 of a self-directed research track on LLM judges, oversight and agent safety. An LLM judges ads with the Madison Ad Check rubric (approve / review / block) and states its confidence (0-100). Its answers are scored against a person's hand labels with [Inspect](https://inspect.aisi.org.uk).

## Status (2026-10-21)
| Piece | State |
|---|---|
| Inspect task, prompts, strict parser, metrics | Built; 10 tests pass, including an end-to-end run on Inspect's mock model |
| Dataset | 156 ads: 36 constructed (`data/seed_constructed.jsonl`) + 120 real ad copy fetched locally from Hugging Face |
| Labels | **0 / 156.** Waiting on human labeling (`labeling/GUIDELINES.md`) |
| Real model runs | Not run yet (needs labels and an Anthropic API key) |

## Metrics
| Metric | Meaning |
|---|---|
| `accuracy` | Judge decision matches the human label (invalid answers count as wrong) |
| `confidently_wrong` | Share of all answers that are wrong **and** stated with confidence ≥ 80 |
| `confident_share_of_errors` | Of the wrong answers, how many were confident |
| `ece` | Expected calibration error, 10 equal-width bins (Guo et al., 2017) |
| `invalid` | Answers that weren't valid JSON with an allowed decision and a 0-100 confidence |

## Run
```bash
uv venv --python 3.13 .venv && source .venv/bin/activate && uv pip install -e . pytest
python -m pytest -q                                      # unit + mock end-to-end tests
python scripts/fetch_hf_ads.py --n 120                   # local-only real ads (license unknown: not committed)
python scripts/build_dataset.py                          # merge into data/ads.jsonl, add new ids to labels.csv
python scripts/label.py --labeler Mayank                 # label (a / r / b)
cp .env.example .env  # add ANTHROPIC_API_KEY, then:
set -a && . ./.env && set +a
inspect eval src/cwlab/task.py --model anthropic/claude-haiku-4-5 -T temperature=0
inspect eval src/cwlab/task.py --model anthropic/claude-haiku-4-5 -T temperature=1 --epochs 5   # self-consistency
inspect view                                             # browse logs
```
Dry run without a key: `inspect eval src/cwlab/task.py --model mockllm/model -T fixture=true`.

## Data notes
- **Constructed ads were written by Claude.** Judging them with Claude may be easier or biased; results are always reported separately by `source`.
- **Hugging Face ads** (`jaykin01/advertisement-copy`) have an unknown license: kept local, never committed or quoted at length. They're mostly benign fashion copy, so they test false alarms.
- `category_hint` is what a constructed ad was designed to test. It is never shown to the judge and is not a label.

## Planned sweep (Project 1)
Models: Haiku vs Sonnet · temperature 0 / 0.5 / 1 · prompt `rubric` vs `rubric_examples` · 5-sample majority vote. Report accuracy, confidently-wrong rate, reliability diagram and ECE per setting and per `source`.
