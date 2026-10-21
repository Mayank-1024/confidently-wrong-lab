"""Keyboard labeling for labeling/labels.csv. Shows one unlabeled ad at a time; saves after every answer.
Usage: python scripts/label.py [--labeler Mayank]
"""
import argparse, csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYS = {"a": "auto_approve", "r": "needs_review", "b": "block"}
ap = argparse.ArgumentParser(); ap.add_argument("--labeler", default="Mayank"); a = ap.parse_args()
ads = {d["id"]: d for d in (json.loads(l) for l in (ROOT / "data/ads.jsonl").read_text().splitlines() if l.strip())}
path = ROOT / "labeling/labels.csv"
with path.open() as f:
    rows = list(csv.DictReader(f))

def save():
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "decision", "labeler", "notes"]); w.writeheader(); w.writerows(rows)

todo = [r for r in rows if not r["decision"]]
for n, r in enumerate(todo, 1):
    ad = ads[r["id"]]
    print(f"\n[{n}/{len(todo)}] {ad['id']} · {ad['channel']} · {ad.get('brand', '')}")
    print(f"  copy: {ad['text']}" if "text" in ad else f"  headline: {ad['headline']}\n  body:     {ad['body']}\n  cta:      {ad['cta'] or '(none)'}")
    k = ""
    while k not in ("a", "r", "b", "s", "q"):
        k = input("  a=approve  r=review  b=block  s=skip  q=quit > ").strip().lower()
    if k == "q":
        break
    if k == "s":
        continue
    r.update(decision=KEYS[k], labeler=a.labeler, notes=input("  note (optional) > ").strip())
    save()
done = sum(1 for r in rows if r["decision"])
print(f"\n{done}/{len(rows)} labeled. Saved to {path}")
