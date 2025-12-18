# 📋 如何查看 Streamlit Cloud 完整錯誤日誌

## 步驟 1：找到錯誤日誌

1. **前往 Streamlit Cloud Dashboard**
   - 登入 https://share.streamlit.io/
   - 找到你的應用

2. **點擊應用名稱**進入應用詳情頁

3. **查看部署日誌**
   - 找到 "Logs" 或 "View logs" 按鈕（通常在右上角或部署狀態旁邊）
   - 或直接查看部署時間線中的錯誤訊息

## 步驟 2：查找關鍵錯誤

在日誌中查找：
- 紅色錯誤訊息（通常以 ❗ 或 ❌ 開頭）
- `Traceback (most recent call last)` 開頭的 Python 錯誤
- `ImportError`、`ModuleNotFoundError`、`FileNotFoundError` 等關鍵字

## 步驟 3：常見錯誤模式

### 模式 1：導入錯誤
```
ImportError: cannot import name 'XXX' from 'YYY'
```
或
```
ModuleNotFoundError: No module named 'XXX'
```

**解決方案**：
- 確認文件存在
- 確認 `__init__.py` 存在
- 確認導入路徑正確

### 模式 2：文件讀取錯誤
```
FileNotFoundError: [Errno 2] No such file or directory: 'assets/XXX.json'
```

**解決方案**：
- 確認 JSON 文件已提交到 GitHub
- 確認文件路徑正確

### 模式 3：語法錯誤
```
SyntaxError: invalid syntax
```

**解決方案**：
- 檢查代碼語法
- 確認 Python 版本兼容

## 步驟 4：提供診斷信息

如果還是無法解決，請提供：

1. **完整的錯誤 Traceback**（從 "Traceback" 開始到最後）
2. **最後 50 行日誌**（如果錯誤在日誌中間）
3. **Main file path 設定**
4. **Secrets 配置狀態**（不需要提供實際的 key 值）

## 臨時解決方案：使用最小測試版本

如果問題持續，可以先用最小版本測試：

1. 在 Streamlit Cloud 設置中，將 Main file path 改為：
   ```
   golden_bonus_project/test_minimal_streamlit.py
   ```

2. 如果最小版本可以啟動，說明問題在 `main.py` 的某個特定部分

3. 逐步恢復功能，找出問題所在


