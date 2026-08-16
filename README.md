# AIIntelAgentPro

基于 Python、FastAPI、SQLite 和 DeepSeek 的 AI 资讯分析系统。

## 项目功能

- 文章增删改查
- 关键词、分类、重要程度筛选
- 分页查询
- 文章分析状态查询
- DeepSeek 单篇分析
- 批量文章分析
- 分析结果持久化到 SQLite
- 批量任务状态监控
- 健康检查接口
- 自动化测试

## 技术栈

- Python 3.11
- FastAPI
- SQLite
- DeepSeek API
- Pydantic
- Pytest

## 启动项目

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --port 8003

# 打开API文档 http://127.0.0.1:8003/docs
# 运行测试 pytest -q
