"""Interface for host-specific capture adapters.

A runner must execute one case in an isolated fixture copy and return a
psp.eval-result/v1 object. No network or model runner is bundled here.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping


class EvalRunner(ABC):
    @abstractmethod
    def run(self, case: Mapping[str, Any], variant: str) -> Dict[str, Any]:
        raise NotImplementedError
