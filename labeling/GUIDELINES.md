# Labeling guidelines

You are the ground truth. Label what **you** would decide as a careful marketing-ops reviewer, using the same rubric the judge gets (`src/cwlab/prompts.py`). Don't look at any model's answer first.

| Label | Use when |
|---|---|
| `auto_approve` | Fine to publish as written. Low-risk issues (mild urgency, a generic CTA) are OK |
| `needs_review` | A person should fix something first: an unproven comparative ("best", "unbeatable"), a missing or very weak CTA, a channel-limit or format problem |
| `block` | Must not publish: placeholder text, false or legally risky claims (health, guarantees, "#1 in the US", fake prices), offensive tone, or text aimed at a reviewer or AI |

Rules:
- One decision per ad. If you hesitate between two labels, pick the stricter one and write why in `notes`.
- `category_hint` on constructed ads is what the ad was designed to test, not the answer. Disagree with it freely.
- Hugging Face ads have no separate headline or CTA; judge the whole copy block.
- Re-label 20 hard cases a day later without looking. Disagreement with yourself is real data (record it in notes as `relabel: <decision>`).
- Labels are never written by a model.

Tool: `python scripts/label.py` (keys: a = approve, r = review, b = block, s = skip, q = quit; progress saves after every ad).
