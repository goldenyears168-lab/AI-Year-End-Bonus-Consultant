# core/pipeline.py
from typing import List, Dict, Any
from core.base_node import BaseNode

class Pipeline:
    def __init__(self):
        self.nodes: List[BaseNode] = [] # 準備一個空的清單來放節點

    def add_node(self, node: BaseNode):
        self.nodes.append(node)
        return self # 讓我們可以寫 .add().add() 這種鍊式語法

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 這是最關鍵的迴圈：像大隊接力一樣傳遞 context
        for node in self.nodes:
            try:
                context = node.execute(context) # 接棒！
            except Exception as e:
                # 把錯誤記下來，不要讓程式崩潰；同時提供 UI 可直接顯示的訊息
                context["error"] = f"{node.name}: {e}"
                context.setdefault("ai_response", f"⚠️ 系統錯誤：{context['error']}")
                break # 停止產線
        return context

