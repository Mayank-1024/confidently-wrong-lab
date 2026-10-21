"""Strict parsing of the judge's answer. Anything malformed is counted as invalid, never guessed."""
import json
import re
from dataclasses import dataclass
from typing import Optional

from .prompts import DECISIONS


@dataclass
class Judgement:
    decision: Optional[str]
    confidence: Optional[float]  # 0-1
    reason: str
    valid: bool
    problem: str = ""


def parse_judgement(text: str) -> Judgement:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return Judgement(None, None, "", False, "no_json")
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return Judgement(None, None, "", False, "malformed_json")
    decision, conf = d.get("decision"), d.get("confidence")
    if decision not in DECISIONS:
        return Judgement(None, None, str(d.get("reason", "")), False, "invalid_decision")
    if not isinstance(conf, (int, float)) or isinstance(conf, bool) or not 0 <= conf <= 100:
        return Judgement(decision, None, str(d.get("reason", "")), False, "invalid_confidence")
    return Judgement(decision, float(conf) / 100.0, str(d.get("reason", "")), True)
