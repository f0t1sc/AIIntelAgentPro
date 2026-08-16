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
- GitHub Actions 自动运行测试
- 运行日志记录

## 技术栈

- Python 3.11
- FastAPI
- SQLite
- DeepSeek API
- Pydantic
- Pytest

## 项目结构

```text
AIIntelAgentPro/
├── app.py
├── database.py
├── analyzer.py
├── test_app.py
├── requirements.txt
├── .env.example
├── README.md
├── .gitignore
└── .github/
    └── workflows/
        └── test.yml
```

## 安装依赖

```powershell
pip install -r requirements.txt
```

## 配置环境变量

复制配置模板：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`：

```env
DEEPSEEK_API_KEY=你的真实API密钥
DEEPSEEK_MODEL=deepseek-v4-flash
```

不要将真实的 `.env` 文件上传到 GitHub。

## 启动项目

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --port 8003
```

打开 API 文档：

```text
http://127.0.0.1:8003/docs
```

## 运行测试

```powershell
pytest -q
```

## 主要接口

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/` | 首页 |
| GET | `/health` | 健康检查 |
| GET | `/articles` | 查询文章 |
| POST | `/articles` | 新增文章 |
| GET | `/articles/{article_id}` | 查询单篇文章 |
| PUT | `/articles/{article_id}` | 修改文章 |
| DELETE | `/articles/{article_id}` | 删除文章 |
| GET | `/stats` | 获取统计信息 |
| POST | `/articles/{article_id}/analyze` | 分析单篇文章 |
| GET | `/articles/{article_id}/analysis` | 查询分析结果 |
| POST | `/analysis/batch` | 批量分析文章 |
| GET | `/analysis/batch/status` | 查询批量分析状态 |

## 文章筛选

`GET /articles` 支持以下参数：

```text
keyword
category
min_importance
analyzed
limit
offset
```

例如：

```text
/articles?keyword=AI&analyzed=false&limit=5
```

## AI 分析流程

```text
读取文章
    ↓
调用 DeepSeek API
    ↓
生成摘要、分类、重要程度和关键词
    ↓
保存分析结果到 SQLite
    ↓
通过 API 返回结果
```

## 自动化测试

项目使用 Pytest 测试：

- 首页接口
- 文章列表接口
- 已分析文章筛选
- 未分析文章筛选
- 健康检查接口
- 不存在文章的错误处理
- 不存在分析结果的错误处理

## 注意事项

以下文件不会提交到 GitHub：

```text
.env
.venv/
articles.db
__pycache__/
```

API Key 只能放在 `.env` 文件中，不要直接写进 Python 代码。