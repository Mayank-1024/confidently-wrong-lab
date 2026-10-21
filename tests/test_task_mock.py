"""End to end on Inspect's mock model: the real task, prompt, parser, scorer and metrics."""
from inspect_ai import eval as inspect_eval
from inspect_ai.model import ModelOutput, get_model

from cwlab.task import confidently_wrong_judge

SCRIPT = {  # matched on ad text, because samples run in parallel
    "Soft Merino Knits": '{"decision": "auto_approve", "confidence": 95, "reason": "fits"}',          # right
    "The #1 blouse": '{"decision": "needs_review", "confidence": 90, "reason": "claims"}',            # wrong, confident
    "ankle boot edit": '{"decision": "needs_review", "confidence": 60, "reason": "too long"}',        # right
    "Unbeatable prices": "Looks fine to me.",                                                         # invalid
}


def scripted(messages, tools, tool_choice, config):
    text = messages[-1].text
    reply = next(v for k, v in SCRIPT.items() if k in text)
    return ModelOutput.from_content(model="mockllm/model", content=reply)


def test_task_end_to_end_on_mock_model():
    model = get_model("mockllm/model", custom_outputs=scripted)
    log = inspect_eval(confidently_wrong_judge(fixture=True), model=model, display="none", log_dir="logs/tests")[0]
    assert log.status == "success"
    m = {k: v.value for k, v in log.results.scores[0].metrics.items()}
    assert m["accuracy"] == 0.5
    assert m["confidently_wrong"] == 0.25
    assert m["confident_share_of_errors"] == 1.0
    assert m["invalid"] == 0.25
    assert abs(m["ece"] - (2 / 3 * 0.425 + 1 / 3 * 0.4)) < 1e-9
