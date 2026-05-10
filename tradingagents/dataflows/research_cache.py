import hashlib
import json
import os
import time
from typing import Any, Dict, Optional


DEFAULT_TTL_SECONDS = 3600


def get_research_cache_ttl(config: Dict[str, Any]) -> int:
    return int(config.get("research_cache_ttl_seconds", DEFAULT_TTL_SECONDS))


def _cache_dir(config: Dict[str, Any], namespace: str) -> str:
    root_dir = config.get("research_cache_dir") or os.path.join(
        config["data_cache_dir"], "research_cache"
    )
    return os.path.join(root_dir, namespace)


def _cache_path(config: Dict[str, Any], namespace: str, key_parts: Dict[str, Any]) -> str:
    key_json = json.dumps(key_parts, sort_keys=True, separators=(",", ":"))
    key_hash = hashlib.sha256(key_json.encode("utf-8")).hexdigest()
    return os.path.join(_cache_dir(config, namespace), f"{key_hash}.json")


def load_text_cache(
    config: Dict[str, Any],
    namespace: str,
    key_parts: Dict[str, Any],
    ttl_seconds: Optional[int] = None,
    now: Optional[float] = None,
) -> Optional[str]:
    path = _cache_path(config, namespace, key_parts)
    if not os.path.exists(path):
        return None

    now = time.time() if now is None else now
    ttl_seconds = get_research_cache_ttl(config) if ttl_seconds is None else ttl_seconds

    try:
        with open(path, "r") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    if now - float(payload.get("created_at", 0)) > ttl_seconds:
        return None

    value = payload.get("value")
    return value if isinstance(value, str) else None


def store_text_cache(
    config: Dict[str, Any],
    namespace: str,
    key_parts: Dict[str, Any],
    value: str,
    now: Optional[float] = None,
) -> None:
    path = _cache_path(config, namespace, key_parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    payload = {
        "created_at": time.time() if now is None else now,
        "key": key_parts,
        "value": value,
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
