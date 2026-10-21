"""Pure metric functions over (correct, confidence) pairs, so they can be unit-tested without a model.

correct: bool, confidence: 0-1 or None (None = invalid answer; counted as wrong for accuracy,
excluded from calibration).
"""
from typing import Optional, Sequence, Tuple

Pair = Tuple[bool, Optional[float]]
CONFIDENT = 0.80


def accuracy(pairs: Sequence[Pair]) -> float:
    return sum(c for c, _ in pairs) / len(pairs) if pairs else 0.0


def confidently_wrong_rate(pairs: Sequence[Pair], threshold: float = CONFIDENT) -> float:
    """Share of ALL answers that are wrong while stating confidence >= threshold."""
    return sum(1 for c, p in pairs if not c and p is not None and p >= threshold) / len(pairs) if pairs else 0.0


def confidently_wrong_share_of_errors(pairs: Sequence[Pair], threshold: float = CONFIDENT) -> float:
    """Of the wrong answers, how many came with high confidence."""
    wrong = [p for c, p in pairs if not c and p is not None]
    return sum(1 for p in wrong if p >= threshold) / len(wrong) if wrong else 0.0


def expected_calibration_error(pairs: Sequence[Pair], bins: int = 10) -> float:
    """ECE (Guo et al., 2017): weighted mean |accuracy - confidence| over equal-width confidence bins."""
    valid = [(c, p) for c, p in pairs if p is not None]
    if not valid:
        return 0.0
    total, ece = len(valid), 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        in_bin = [(c, p) for c, p in valid if (lo <= p < hi) or (b == bins - 1 and p == 1.0)]
        if in_bin:
            acc = sum(c for c, _ in in_bin) / len(in_bin)
            conf = sum(p for _, p in in_bin) / len(in_bin)
            ece += len(in_bin) / total * abs(acc - conf)
    return ece


def invalid_rate(pairs: Sequence[Pair]) -> float:
    return sum(1 for _, p in pairs if p is None) / len(pairs) if pairs else 0.0
