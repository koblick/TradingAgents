import time

from tradingagents.dataflows.research_cache import load_text_cache, store_text_cache


def test_text_cache_returns_value_within_ttl(tmp_path):
    config = {"data_cache_dir": str(tmp_path)}
    key_parts = {"tool": "get_stock_news_openai", "ticker": "MU", "date": "2026-05-08"}
    now = time.time()

    store_text_cache(config, "openai_search", key_parts, "cached report", now=now)

    assert (
        load_text_cache(
            config,
            "openai_search",
            key_parts,
            ttl_seconds=3600,
            now=now + 120,
        )
        == "cached report"
    )


def test_text_cache_misses_after_ttl(tmp_path):
    config = {"data_cache_dir": str(tmp_path)}
    key_parts = {"tool": "get_global_news_openai", "date": "2026-05-08"}
    now = time.time()

    store_text_cache(config, "openai_search", key_parts, "stale report", now=now)

    assert (
        load_text_cache(
            config,
            "openai_search",
            key_parts,
            ttl_seconds=3600,
            now=now + 3601,
        )
        is None
    )


def test_text_cache_key_includes_all_parts(tmp_path):
    config = {"data_cache_dir": str(tmp_path)}
    base_key = {"tool": "get_fundamentals_openai", "ticker": "MU", "date": "2026-05-08"}
    other_key = {"tool": "get_fundamentals_openai", "ticker": "HIMS", "date": "2026-05-08"}
    now = time.time()

    store_text_cache(config, "openai_search", base_key, "mu report", now=now)

    assert (
        load_text_cache(
            config,
            "openai_search",
            other_key,
            ttl_seconds=3600,
            now=now,
        )
        is None
    )
