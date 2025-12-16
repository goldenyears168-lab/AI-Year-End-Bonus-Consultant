# assets/knowledge.py
# 年終獎金發放顧問知識庫

import json
import os
from pathlib import Path

def load_knowledge_from_json():
    """
    從多個 JSON 文件讀取知識庫內容並格式化為文本
    支持新格式：1-company_info.json, 2-ai_config.json, 3-knowledge_base.json
    也支持舊格式：knowledge.json（向後兼容）
    """
    current_dir = Path(__file__).parent
    
    # 嘗試加載新格式（多文件）
    company_info_path = current_dir / "1-company_info.json"
    ai_config_path = current_dir / "2-ai_config.json"
    knowledge_base_path = current_dir / "3-knowledge_base.json"
    
    kb_data = {}
    errors = []
    
    # 加載公司信息
    if company_info_path.exists():
        try:
            with open(company_info_path, 'r', encoding='utf-8') as f:
                kb_data['company_info'] = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"公司信息 JSON 解析錯誤: {str(e)}")
    else:
        errors.append("找不到 1-company_info.json")
    
    # 加載 AI 配置
    if ai_config_path.exists():
        try:
            with open(ai_config_path, 'r', encoding='utf-8') as f:
                kb_data['ai_config'] = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"AI 配置 JSON 解析錯誤: {str(e)}")
    else:
        errors.append("找不到 2-ai_config.json")
    
    # 加載知識庫（主要內容）
    if knowledge_base_path.exists():
        try:
            with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                kb_main = json.load(f)
                # 將知識庫內容合併到主數據結構
                kb_data.update(kb_main)
        except json.JSONDecodeError as e:
            errors.append(f"知識庫 JSON 解析錯誤: {str(e)}")
    else:
        # 向後兼容：嘗試加載舊格式
        old_json_path = current_dir / "knowledge.json"
        if old_json_path.exists():
            try:
                with open(old_json_path, 'r', encoding='utf-8') as f:
                    kb_main = json.load(f)
                    kb_data.update(kb_main)
            except json.JSONDecodeError as e:
                errors.append(f"舊知識庫 JSON 解析錯誤: {str(e)}")
        else:
            errors.append("找不到 3-knowledge_base.json 或 knowledge.json")
    
    if errors and not kb_data:
        # 如果所有文件都失敗，返回錯誤信息
        return f"⚠️ 知識庫加載失敗:\n" + "\n".join(f"- {e}" for e in errors)
    
    # 格式化為文本
    return format_knowledge_json(kb_data)

def format_knowledge_json(kb_data):
    """
    將 JSON 知識庫數據格式化為 Markdown 文本
    支持新格式（包含 company_info 和 ai_config）和舊格式
    """
    lines = []
    
    # 0. 工具介紹（來自 company_info）
    if 'company_info' in kb_data:
        company_info = kb_data['company_info']
        lines.append("# 年終獎金發放顧問工具 (Year-End Bonus Strategic Advisor)")
        lines.append("")
        lines.append(f"**工具名稱**: {company_info.get('tool_name', 'N/A')} ({company_info.get('tool_name_en', 'N/A')})")
        lines.append(f"**版本**: {company_info.get('version', 'N/A')}")
        lines.append(f"**更新日期**: {company_info.get('last_updated', 'N/A')}")
        lines.append("")
        lines.append(f"**描述**: {company_info.get('description', 'N/A')}")
        lines.append("")
        lines.append(f"**目標用戶**: {company_info.get('target_audience', 'N/A')}")
        lines.append("")
        
        if 'key_features' in company_info:
            lines.append("**核心功能**:")
            for feature in company_info['key_features']:
                lines.append(f"- {feature}")
            lines.append("")
        
        if 'input_requirements' in company_info:
            lines.append("**輸入需求**:")
            for req in company_info['input_requirements']:
                lines.append(f"- {req}")
            lines.append("")
        
        if 'output_provides' in company_info:
            lines.append("**輸出內容**:")
            for output in company_info['output_provides']:
                lines.append(f"- {output}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 1. 元數據（來自知識庫主文件）
    lines.append("## 知識庫元數據 (Knowledge Base Metadata)")
    lines.append("")
    lines.append(f"**知識庫 ID**: {kb_data.get('kb_id', 'N/A')}")
    lines.append(f"**版本**: {kb_data.get('version', 'N/A')}")
    lines.append(f"**標題**: {kb_data.get('title', 'N/A')}")
    lines.append(f"**用途**: {kb_data.get('purpose', 'N/A')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 1.5. AI 配置（意圖和實體提取）
    if 'ai_config' in kb_data:
        ai_config = kb_data['ai_config']
        lines.append("## AI 配置 (AI Configuration)")
        lines.append("")
        
        if 'intents' in ai_config:
            lines.append("### 意圖識別 (Intent Recognition)")
            lines.append("")
            for intent in ai_config['intents']:
                intent_id = intent.get('id', '')
                comment = intent.get('_comment', '')
                keywords = intent.get('keywords', [])
                if comment:
                    lines.append(f"**{intent_id}**: {comment}")
                else:
                    lines.append(f"**{intent_id}**")
                if keywords:
                    lines.append(f"- 關鍵詞: {', '.join(keywords)}")
                lines.append("")
        
        if 'entity_patterns' in ai_config:
            lines.append("### 實體提取模式 (Entity Extraction Patterns)")
            lines.append("")
            for pattern_type, patterns in ai_config['entity_patterns'].items():
                if pattern_type.startswith('_'):
                    continue
                lines.append(f"**{pattern_type}**:")
                if isinstance(patterns, list):
                    for pattern in patterns:
                        pattern_id = pattern.get('id', '')
                        pattern_keywords = pattern.get('keywords', [])
                        if pattern_id and pattern_keywords:
                            lines.append(f"- {pattern_id}: {', '.join(pattern_keywords)}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 2. 實體定義
    if 'entities' in kb_data:
        entities = kb_data['entities']
        lines.append("## 實體定義 (Entity Definitions)")
        lines.append("")
        
        # 枚舉類型
        if 'enums' in entities:
            lines.append("### 枚舉類型 (Enums)")
            lines.append("")
            for enum_name, enum_values in entities['enums'].items():
                lines.append(f"**{enum_name}**:")
                if isinstance(enum_values, list):
                    lines.append("- " + ", ".join(str(v) for v in enum_values))
                else:
                    lines.append(f"- {enum_values}")
                lines.append("")
        
        # 表格數據
        if 'tables' in entities:
            lines.append("### 配置表格 (Configuration Tables)")
            lines.append("")
            
            # StageConfig
            if 'StageConfig' in entities['tables']:
                lines.append("#### 企業發展階段配置 (StageConfig)")
                lines.append("")
                lines.append("| 階段 | 名稱 | HR Ratio 範圍 | 總獎金比例 | 季獎金 | 年終獎金 | 說明 |")
                lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
                for stage_key, stage_data in entities['tables']['StageConfig'].items():
                    name = stage_data.get('name', '')
                    hr_range = stage_data.get('hrRatioRange', {})
                    hr_min = hr_range.get('min', 0) * 100
                    hr_max = hr_range.get('max', 0) * 100
                    bonus = stage_data.get('bonus', {})
                    total = bonus.get('totalBonusRatio', 0) * 100
                    quarterly = bonus.get('quarterly', 0) * 100
                    year_end = bonus.get('yearEnd', 0) * 100
                    desc = stage_data.get('description', '')
                    lines.append(f"| {stage_key} | {name} | {hr_min:.0f}%-{hr_max:.0f}% | {total:.0f}% | {quarterly:.1f}% | {year_end:.0f}% | {desc} |")
                lines.append("")
            
            # EngineToDepartmentWeights
            if 'EngineToDepartmentWeights' in entities['tables']:
                lines.append("#### 增長引擎與部門權重 (EngineToDepartmentWeights)")
                lines.append("")
                for engine_key, engine_data in entities['tables']['EngineToDepartmentWeights'].items():
                    lines.append(f"**{engine_key}** (增長引擎):")
                    lines.append("")
                    weights = engine_data.get('weights', {})
                    reasons = engine_data.get('reasons', {})
                    lines.append("| 部門 | 權重 | 說明 |")
                    lines.append("| :--- | :--- | :--- |")
                    for dept, weight in weights.items():
                        reason = reasons.get(dept, '')
                        lines.append(f"| {dept} | {weight} | {reason} |")
                    lines.append("")
            
            # IndustryCategoryInfo
            if 'IndustryCategoryInfo' in entities['tables']:
                lines.append("#### 行業類別資訊 (IndustryCategoryInfo)")
                lines.append("")
                for cat_key, cat_info in entities['tables']['IndustryCategoryInfo'].items():
                    icon = cat_info.get('icon', '')
                    name = cat_info.get('name', '')
                    lines.append(f"- {icon} **{cat_key}**: {name}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 3. 規則（頂層）
    if 'rules' in kb_data:
        lines.append("## 計算規則 (Calculation Rules)")
        lines.append("")
        for rule_key, rule_data in kb_data['rules'].items():
            title = rule_data.get('title', rule_key)
            inputs = rule_data.get('inputs', [])
            formula = rule_data.get('formula', '')
            outputs = rule_data.get('outputs', [])
            notes = rule_data.get('notes', '')
            
            lines.append(f"### {title} ({rule_key})")
            lines.append("")
            if inputs:
                lines.append(f"**輸入**: {', '.join(inputs)}")
            if outputs:
                lines.append(f"**輸出**: {', '.join(outputs)}")
            if formula:
                lines.append(f"**公式**: `{formula}`")
            if notes:
                lines.append(f"**說明**: {notes}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 4. 腳本（頂層）
    if 'scripts' in kb_data:
        lines.append("## 溝通腳本 (Communication Scripts)")
        lines.append("")
        for script_key, script_data in kb_data['scripts'].items():
            title = script_data.get('title', script_key)
            when = script_data.get('when', '')
            text = script_data.get('text', '')
            
            lines.append(f"### {title} ({script_key})")
            lines.append("")
            if when:
                lines.append(f"**觸發條件**: {when}")
                lines.append("")
            if text:
                lines.append(f"**話術**: {text}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 5. 範例（頂層）
    if 'examples' in kb_data:
        lines.append("## 計算範例 (Calculation Examples)")
        lines.append("")
        for example_key, example_data in kb_data['examples'].items():
            title = example_data.get('title', example_key)
            scenario = example_data.get('scenario', '')
            calculation = example_data.get('calculation', '')
            output = example_data.get('output', '')
            notes = example_data.get('notes', '')
            
            lines.append(f"### {title} ({example_key})")
            lines.append("")
            if scenario:
                lines.append(f"**情境**: {scenario}")
                lines.append("")
            if calculation:
                lines.append(f"**計算過程**: {calculation}")
                lines.append("")
            if output:
                lines.append(f"**結果**: {output}")
                lines.append("")
            if notes:
                lines.append(f"**備註**: {notes}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 6. 檢索塊（知識塊）
    if 'retrieval' in kb_data and 'chunks' in kb_data['retrieval']:
        lines.append("## 知識塊 (Knowledge Chunks)")
        lines.append("")
        lines.append("以下知識塊用於回答常見問題：")
        lines.append("")
        
        for chunk in kb_data['retrieval']['chunks']:
            chunk_id = chunk.get('chunk_id', '')
            title = chunk.get('title', '')
            tags = chunk.get('tags', [])
            q_triggers = chunk.get('q_triggers', [])
            content = chunk.get('content', '')
            
            lines.append(f"### {title} ({chunk_id})")
            lines.append("")
            if tags:
                lines.append(f"**標籤**: {', '.join(tags)}")
                lines.append("")
            if q_triggers:
                lines.append("**相關問題**:")
                for q in q_triggers:
                    lines.append(f"- {q}")
                lines.append("")
            if content:
                lines.append(f"**內容**: {content}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)

# 從 JSON 加載知識庫
BONUS_KB_TEXT = load_knowledge_from_json()
