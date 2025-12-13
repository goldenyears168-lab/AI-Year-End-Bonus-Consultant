# 🔒 安全最佳实践

## ⚠️ 重要：API Key 安全

**永远不要**将 API key 提交到 Git 仓库，即使是私有仓库也不应该。

## ✅ 正确的做法

### 1. 使用环境变量

**本地开发**：使用 `.env` 文件（已在 `.gitignore` 中）
```env
GEMINI_API_KEY=your-actual-api-key-here
```

**Streamlit Cloud**：使用 Secrets（在控制台中设置）

### 2. 文档中使用占位符

在文档、README 或示例代码中，**永远使用占位符**：
- ✅ `your-gemini-api-key-here`
- ✅ `YOUR_API_KEY_HERE`
- ❌ 不要使用真实的 API key

### 3. 检查清单

在提交代码前，运行：
```bash
bash scripts/check-secrets.sh
```

## 🛡️ 如果 API Key 已泄露

1. **立即撤销**：在 Google AI Studio 中删除泄露的 API key
2. **创建新 Key**：生成新的 API key
3. **清理历史**：从 git 历史中移除敏感信息（见 `安全修复指南.md`）
4. **更新所有地方**：更新本地 `.env` 和 Streamlit Cloud Secrets

## 📋 快速检查命令

```bash
# 检查工作目录中是否有 API key
grep -r "AIzaSy" --exclude-dir=venv --exclude-dir=.git .

# 检查 git 历史中是否有 API key
git log -p | grep "AIzaSy"

# 使用检查脚本
bash scripts/check-secrets.sh
```

