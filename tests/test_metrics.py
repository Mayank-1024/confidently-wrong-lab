import pytest
from cwlab import metrics as M

PAIRS = [(True, 0.95), (False, 0.90), (True, 0.60), (False, None)]  # None = invalid answer


def test_accuracy_counts_invalid_as_wrong():
    assert M.accuracy(PAIRS) == 0.5


def test_confidently_wrong_rate_is_share_of_all_answers():
    assert M.confidently_wrong_rate(PAIRS) == 0.25


def test_confident_share_of_errors_ignores_invalid():
    assert M.confidently_wrong_share_of_errors(PAIRS) == 1.0


def test_ece_matches_hand_calculation():
    # bin 0.9-1.0: acc 0.5, conf 0.925, weight 2/3; bin 0.6-0.7: acc 1, conf 0.6, weight 1/3
    assert M.expected_calibration_error(PAIRS) == pytest.approx(2 / 3 * 0.425 + 1 / 3 * 0.4)


def test_ece_zero_when_perfectly_calibrated():
    assert M.expected_calibration_error([(True, 1.0), (True, 1.0)]) == pytest.approx(0.0)


def test_invalid_rate_and_empty_inputs():
    assert M.invalid_rate(PAIRS) == 0.25
    assert M.accuracy([]) == 0.0 and M.expected_calibration_error([]) == 0.0
