# 🔧 Streamlit Cloud API Key 故障排除指南

## 📋 问题症状

更新 Streamlit Cloud Secrets 中的 `GEMINI_API_KEY` 后，应用仍然显示错误：
```
⚠️ AI 連線錯誤: 400 API key expired. Please renew the API key.
```

## ✅ 解决方案（按顺序尝试）

### 步骤 1：确认 Secrets 格式正确

在 Streamlit Cloud 的 Secrets 中，确保格式为 **TOML** 格式：

```toml
GEMINI_API_KEY = "AIzaSyBXtR92jUgrhxaxF7_sC6DN1RnwIiAxT_8"
```

**重要检查点**：
- ✅ Key 名称完全一致：`GEMINI_API_KEY`（大小写敏感）
- ✅ 使用双引号包裹值
- ✅ 没有多余的空格或换行
- ✅ 点击了 "Save changes" 按钮

### 步骤 2：等待 Secrets 传播

Streamlit Cloud 的 Secrets 更新后需要 **约 1-2 分钟** 才能传播到应用。

**操作**：
1. 保存 Secrets 后，等待 1-2 分钟
2. 刷新应用页面
3. 重新测试

### 步骤 3：重启应用

如果等待后仍然失败，需要重启应用：

1. 前往 Streamlit Cloud 控制台
2. 找到您的应用
3. 点击右上角的 **"⋮" (三个点)** 菜单
4. 选择 **"Restart app"** 或 **"Redeploy"**
5. 等待应用重启完成（约 30 秒 - 1 分钟）

### 步骤 4：验证 API Key 有效性

确认 API Key 本身是有效的：

1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 检查 API Key 是否仍然有效
3. 如果已过期，创建新的 API Key
4. 更新 Streamlit Cloud Secrets

### 步骤 5：检查代码更新

确保代码已更新到最新版本（已修复 API Key 读取逻辑）：

**已修复的问题**：
- ✅ 优先使用 `st.secrets`（Streamlit Cloud）
- ✅ 动态读取 API Key（每次调用时重新读取）
- ✅ 更好的错误处理

**确认方法**：
1. 检查 `utils/gemini_client.py` 文件
2. 确认包含 `get_api_key()` 函数
3. 确认 `call_gemini_logic()` 函数中动态获取 API Key

### 步骤 6：查看应用日志

如果以上步骤都无效，查看应用日志：

1. 在 Streamlit Cloud 控制台中
2. 点击应用的 **"Manage app"**
3. 查看 **"Logs"** 标签
4. 查找错误信息，特别是：
   - `未找到 GEMINI_API_KEY`
   - `API key expired`
   - 其他相关错误

## 🔍 常见问题

### Q1: 为什么更新 Secrets 后还是显示旧错误？

**A**: Streamlit Cloud 需要时间传播 Secrets，并且应用可能缓存了旧的配置。请：
1. 等待 1-2 分钟
2. 重启应用
3. 清除浏览器缓存并刷新

### Q2: 本地测试正常，但云端失败？

**A**: 这通常是因为：
1. Secrets 格式不正确（TOML 格式）
2. Key 名称不匹配（大小写敏感）
3. 应用没有重启

### Q3: 如何确认 Secrets 已正确设置？

**A**: 在应用代码中添加临时调试代码（仅用于测试）：

```python
# 在 main.py 开头添加（测试用，完成后删除）
import streamlit as st
st.write("API Key 前10个字符:", st.secrets.get("GEMINI_API_KEY", "NOT FOUND")[:10])
```

### Q4: API Key 格式要求是什么？

**A**: 
- 在 Streamlit Cloud Secrets 中：使用 TOML 格式，带双引号
- 在本地 `.env` 文件中：直接赋值，不需要引号

**正确格式**：
```toml
# Streamlit Cloud Secrets (TOML)
GEMINI_API_KEY = "AIzaSyBXtR92jUgrhxaxF7_sC6DN1RnwIiAxT_8"
```

```env
# 本地 .env 文件
GEMINI_API_KEY=AIzaSyBXtR92jUgrhxaxF7_sC6DN1RnwIiAxT_8
```

## 📝 检查清单

在报告问题前，请确认：

- [ ] Secrets 格式正确（TOML，带双引号）
- [ ] Key 名称完全一致：`GEMINI_API_KEY`
- [ ] 已点击 "Save changes"
- [ ] 已等待 1-2 分钟让 Secrets 传播
- [ ] 已重启应用
- [ ] API Key 在 Google AI Studio 中验证有效
- [ ] 代码已更新到最新版本
- [ ] 已查看应用日志

## 🆘 如果仍然无法解决

1. **检查 GitHub 仓库**：
   - 确认代码已推送到 GitHub
   - 确认 Streamlit Cloud 连接到正确的分支

2. **重新部署**：
   - 在 Streamlit Cloud 中删除应用
   - 重新创建并部署
   - 重新设置 Secrets

3. **联系支持**：
   - Streamlit Cloud 支持：https://discuss.streamlit.io/
   - 或查看 Streamlit 官方文档

## ✅ 成功标志

当一切正常时，您应该看到：
- ✅ 应用正常加载
- ✅ 可以生成决策备忘录
- ✅ AI 聊天功能正常工作
- ✅ 没有 API Key 相关错误

