import json
import os
from datetime import datetime, timezone
from typing import Any, Optional


class ProgressLogger:
    def __init__(self, path: Optional[str]):
        self.path = path

    def log(self, event: str, **fields: Any) -> None:
        if not self.path:
            return

        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **fields,
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(payload, default=str) + "\n")
            f.flush()
