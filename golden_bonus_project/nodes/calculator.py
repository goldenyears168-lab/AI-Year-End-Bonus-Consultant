# nodes/calculator.py
from core.base_node import BaseNode
from typing import Dict, Any

class CalculatorNode(BaseNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        data = context["user_input"]
        
        # 1. 安全檢查：避免除以零的錯誤 (Edge Case)
        if data["employees"] <= 0:
            raise ValueError("員工人數不能為 0 或負數")
        if data["avg_salary"] <= 0:
            raise ValueError("平均月薪不能為 0 或負數")

        # 2. 核心公式
        # 獎金池 = 淨利 * (1 - 保留比例)
        # 注意：保留比例包含股東分潤與明年營運週轉金（簡化模型）
        # net_profit 單位是萬元，需要轉換為元
        pool = (data["net_profit"] * 10000) * (1 - data["retention_rate"])
        
        # 人均 = 獎金池 / 人數
        per_head = pool / data["employees"]
        
        # 月數 = 人均 / 月薪
        months = per_head / data["avg_salary"]

        # 3. 寫入 Metrics
        context["metrics"] = {
            "total_pool": int(pool),
            "per_head": int(per_head),
            "months": round(months, 2) # 取小數點後兩位
        }
        
        # 4. 風險檢查（精實：直接在這裡檢查，不單獨建立節點）
        risks = []
        
        # 規則 1: 發太少 (低於 0.5 個月)
        if months < 0.5:
            risks.append("⚠️ **紅色警報**：平均獎金低於 0.5 個月，根據統計，這會導致年後離職率上升 30%。")
        
        # 規則 2: 發太多 (透支保留盈餘)
        # 假設我們不希望老闆保留盈餘低於 10%
        if data["retention_rate"] < 0.1:
            risks.append("⚠️ **財務警告**：您的保留盈餘過低，公司現金流抗風險能力將減弱。")
        
        context["risks"] = risks
        
        return context

