"""Fetch a fixed random sample of real ad copy from jaykin01/advertisement-copy (Hugging Face).

The dataset's license is listed as unknown, so the output stays LOCAL: data/hf_ads.local.jsonl is
git-ignored and its text must not be published or quoted at length. Channels are assigned
deterministically, because the dataset has none.

Usage: python scripts/fetch_hf_ads.py [--n 120] [--seed 7]
"""
import argparse, json, random, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://datasets-server.huggingface.co/rows?dataset=jaykin01/advertisement-copy&config=default&split=train&offset={o}&length=100"
CHANNELS = ["Google Ads", "Facebook", "Instagram", "YouTube", "Email", "Website"]

ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=120); ap.add_argument("--seed", type=int, default=7); a = ap.parse_args()
rows, offset = [], 0
while True:
    d = json.load(urllib.request.urlopen(API.format(o=offset)))
    rows += [r["row"] for r in d["rows"]]
    offset += 100
    if offset >= d["num_rows_total"]:
        break
rows = [r for r in rows if (r.get("ad") or "").strip()]
rng = random.Random(a.seed)
pick = rng.sample(range(len(rows)), a.n)
out = ROOT / "data/hf_ads.local.jsonl"
with out.open("w") as f:
    for k, i in enumerate(sorted(pick)):
        r = rows[i]
        f.write(json.dumps({"id": f"hf-{i:04d}", "channel": CHANNELS[k % len(CHANNELS)], "brand": (r.get("product") or "").strip(),
                            "text": r["ad"].strip(), "source": "hf:jaykin01/advertisement-copy"}) + "\n")
print(f"{a.n} of {len(rows)} ads -> {out} (local only)")
