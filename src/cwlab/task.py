"""Project 1, Confidently Wrong: an Inspect eval of an LLM ad judge against Mayank's hand labels.

Run (real):   inspect eval src/cwlab/task.py --model anthropic/claude-haiku-4-5 -T temperature=0
Sweep knobs:  -T prompt=rubric|rubric_examples  -T temperature=0|0.5|1  --epochs 5 (self-consistency)
Dry run:      inspect eval src/cwlab/task.py --model mockllm/model -T fixture=true

Only ads that have a human label are evaluated. Labels are the ground truth and are written by a
person (labeling/GUIDELINES.md), never by a model.
"""
import csv
import json
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import ChatMessageSystem, GenerateConfig
from inspect_ai.scorer import CORRECT, INCORRECT, Score, SampleScore, Target, accuracy, metric, scorer, stderr, value_to_float
from inspect_ai.solver import Generate, TaskState, generate, solver

from cwlab import metrics as M
from cwlab.parse import parse_judgement
from cwlab.prompts import DECISIONS, VARIANTS, render_ad

ROOT = Path(__file__).resolve().parents[2]


def load_samples(ads_path: Path, labels_path: Path) -> list[Sample]:
    ads = {}
    for line in ads_path.read_text().splitlines():
        if line.strip():
            ad = json.loads(line)
            ads[ad["id"]] = ad
    samples = []
    with labels_path.open() as f:
        for row in csv.DictReader(f):
            label = (row.get("decision") or "").strip()
            if not label:
                continue  # not labeled yet
            if label not in DECISIONS:
                raise ValueError(f"{row['id']}: label {label!r} is not one of {DECISIONS}")
            ad = ads[row["id"]]
            samples.append(Sample(id=ad["id"], input=render_ad(ad), target=label,
                                  metadata={"channel": ad["channel"], "source": ad.get("source", ""),
                                            "category_hint": ad.get("category_hint", ""), "labeler": row.get("labeler", "")}))
    if not samples:
        raise ValueError(f"No labeled ads in {labels_path}. Label some first (labeling/GUIDELINES.md).")
    return samples


@solver
def judge_system(prompt: str):
    """Insert the judge prompt verbatim (system_message() would treat the JSON braces as template fields)."""
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.messages.insert(0, ChatMessageSystem(content=VARIANTS[prompt]))
        return state
    return solve


_as_float = value_to_float()


def _pairs(scores: list[SampleScore]):
    # Inspect may hand metrics the value as "C"/"I" or already converted to 1.0/0.0; normalise both.
    return [(_as_float(s.score.value) == 1.0, (s.score.metadata or {}).get("confidence")) for s in scores]


@metric
def confidently_wrong():
    def compute(scores: list[SampleScore]) -> float:
        return M.confidently_wrong_rate(_pairs(scores))
    return compute


@metric
def confident_share_of_errors():
    def compute(scores: list[SampleScore]) -> float:
        return M.confidently_wrong_share_of_errors(_pairs(scores))
    return compute


@metric
def ece():
    def compute(scores: list[SampleScore]) -> float:
        return M.expected_calibration_error(_pairs(scores))
    return compute


@metric
def invalid():
    def compute(scores: list[SampleScore]) -> float:
        return M.invalid_rate(_pairs(scores))
    return compute


@scorer(metrics=[accuracy(), stderr(), confidently_wrong(), confident_share_of_errors(), ece(), invalid()])
def judge_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        j = parse_judgement(state.output.completion)
        correct = j.valid and j.decision == target.text
        return Score(value=CORRECT if correct else INCORRECT, answer=j.decision or "",
                     explanation=j.reason or j.problem,
                     metadata={"confidence": j.confidence, "valid": j.valid, "problem": j.problem, "decision": j.decision})
    return score


@task
def confidently_wrong_judge(prompt: str = "rubric", temperature: float = 0.0, fixture: bool = False,
                            ads: str = "data/ads.jsonl", labels: str = "labeling/labels.csv"):
    if fixture:
        ads, labels = "tests/fixtures/ads.jsonl", "tests/fixtures/labels.csv"
    if prompt not in VARIANTS:
        raise ValueError(f"prompt must be one of {list(VARIANTS)}")
    return Task(dataset=MemoryDataset(load_samples(ROOT / ads, ROOT / labels), name="cw-ads"),
                solver=[judge_system(prompt), generate()],
                scorer=judge_scorer(),
                config=GenerateConfig(temperature=temperature, max_tokens=400))
