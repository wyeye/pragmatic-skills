"""Replay already captured psp.eval-result/v1 JSON without calling a model."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Mapping
from .base import EvalRunner


class ReplayRunner(EvalRunner):
    def __init__(self, captures: Path):
        payload = json.loads(captures.read_text(encoding="utf-8"))
        self.results = {(item["case_id"], item["variant"]): item for item in payload.get("results", payload)}

    def run(self, case: Mapping[str, Any], variant: str) -> Dict[str, Any]:
        return dict(self.results[(case["id"], variant)])
