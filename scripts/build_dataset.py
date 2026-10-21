"""Merge ad sources into data/ads.jsonl and add any new ids to labeling/labels.csv.

Existing labels are never overwritten or reordered; new ads get an empty decision for a person to fill.
Usage: python scripts/build_dataset.py
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [ROOT / "data/seed_constructed.jsonl", ROOT / "data/hf_ads.local.jsonl"]
ads = []
for src in SOURCES:
    if src.exists():
        ads += [json.loads(l) for l in src.read_text().splitlines() if l.strip()]
ids = [a["id"] for a in ads]
assert len(ids) == len(set(ids)), "duplicate ad ids"
(ROOT / "data/ads.jsonl").write_text("".join(json.dumps(a) + "\n" for a in ads))

labels_path = ROOT / "labeling/labels.csv"
existing = []
if labels_path.exists():
    with labels_path.open() as f:
        existing = list(csv.DictReader(f))
have = {r["id"] for r in existing}
new = [{"id": i, "decision": "", "labeler": "", "notes": ""} for i in ids if i not in have]
with labels_path.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "decision", "labeler", "notes"]); w.writeheader(); w.writerows(existing + new)
done = sum(1 for r in existing if r["decision"])
print(f"{len(ads)} ads in data/ads.jsonl | labels: {done} done, {len(existing) + len(new) - done} to go ({len(new)} new)")
