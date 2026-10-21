from cwlab.parse import parse_judgement


def test_valid_answer_with_surrounding_prose():
    j = parse_judgement('Sure. {"decision": "block", "confidence": 92, "reason": "medical claim"}')
    assert j.valid and j.decision == "block" and j.confidence == 0.92


def test_rejects_unknown_decision_and_out_of_range_confidence():
    assert parse_judgement('{"decision": "approve", "confidence": 90, "reason": ""}').problem == "invalid_decision"
    assert parse_judgement('{"decision": "block", "confidence": 140, "reason": ""}').problem == "invalid_confidence"
    assert parse_judgement('{"decision": "block", "confidence": true, "reason": ""}').problem == "invalid_confidence"


def test_no_json_and_malformed_json():
    assert parse_judgement("I think it's fine").problem == "no_json"
    assert parse_judgement('{"decision": block}').problem == "malformed_json"
