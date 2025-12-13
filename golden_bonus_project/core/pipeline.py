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
        print("🚀 Pipeline 開始運作...")
        
        # 這是最關鍵的迴圈：像大隊接力一樣傳遞 context
        for node in self.nodes:
            try:
                print(f"   Running node: {node.name}")
                context = node.execute(context) # 接棒！
            except Exception as e:
                print(f"❌ Error in {node.name}: {e}")
                context["error"] = str(e) # 把錯誤記下來，不要讓程式崩潰
                break # 停止產線
        
        print("✅ Pipeline 完成")
        return context

