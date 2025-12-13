# core/base_node.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseNode(ABC):
    """
    這是所有節點的「爸爸」（父類別）。
    它規定所有繼承它的「孩子」都必須會做 execute 這件事。
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        輸入：context (舊的)
        輸出：context (新的，加上這個節點處理後的結果)
        """
        pass

