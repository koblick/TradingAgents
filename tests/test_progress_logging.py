import json

from tradingagents.progress import ProgressLogger


def test_progress_logger_writes_jsonl_event(tmp_path):
    log_path = tmp_path / "progress.jsonl"
    logger = ProgressLogger(str(log_path))

    logger.log("node_start", node="Market Analyst", ticker="MU")

    payload = json.loads(log_path.read_text().strip())
    assert payload["event"] == "node_start"
    assert payload["node"] == "Market Analyst"
    assert payload["ticker"] == "MU"
    assert "timestamp" in payload


def test_progress_logger_noops_without_path(tmp_path):
    logger = ProgressLogger(None)

    logger.log("node_start", node="Market Analyst")

    assert list(tmp_path.iterdir()) == []


def test_progress_logger_accepts_filename_without_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    logger = ProgressLogger("progress.jsonl")

    logger.log("node_start", node="Market Analyst")

    assert (tmp_path / "progress.jsonl").exists()
