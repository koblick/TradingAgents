import json

from tradingagents.graph.setup import GraphSetup
from tradingagents.progress import ProgressLogger


def test_graph_node_wrapper_logs_start_and_end(tmp_path):
    log_path = tmp_path / "progress.jsonl"
    setup = object.__new__(GraphSetup)
    setup.progress_logger = ProgressLogger(str(log_path))

    wrapped = setup._wrap_node("Test Node", lambda state: {"done": True})

    assert wrapped({"company_of_interest": "MU", "trade_date": "2026-05-08"}) == {
        "done": True
    }

    events = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert [event["event"] for event in events] == ["node_start", "node_end"]
    assert events[0]["node"] == "Test Node"
    assert events[0]["ticker"] == "MU"


def test_graph_node_wrapper_logs_errors(tmp_path):
    log_path = tmp_path / "progress.jsonl"
    setup = object.__new__(GraphSetup)
    setup.progress_logger = ProgressLogger(str(log_path))

    def failing_node(state):
        raise RuntimeError("boom")

    wrapped = setup._wrap_node("Failing Node", failing_node)

    try:
        wrapped({"company_of_interest": "HIMS", "trade_date": "2026-05-08"})
    except RuntimeError:
        pass

    events = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert [event["event"] for event in events] == ["node_start", "node_error"]
    assert events[1]["error_type"] == "RuntimeError"
