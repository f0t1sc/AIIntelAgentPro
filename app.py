from fastapi import FastAPI, HTTPException,Query
from pydantic import BaseModel, Field

from database import(
    create_article,
    get_articles,
    initialize_database,
    get_article,
    get_article_by_title,
    update_article,
    delete_article,
    get_statistics,
    save_analysis,
    get_analysis,
)
from analyzer import analyze_article
from source_client import (
    fetch_dev_articles,
    normalize_dev_articles,
)
from datetime import datetime
import logging
app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

batch_status = {
    "status": "idle",
    "started_at": None,
    "finished_at": None,
    "total": 0,
    "completed": 0,
    "failed": 0,
}

initialize_database()

class ArticleCreate(BaseModel):
    title: str=Field(min_length=1)
    category: str=Field(min_length=1)
    importance:int=Field(ge=1,le=5)
@app.get("/")
def home():
    return {"message": "AIIntelAgent Pro is running"}

@app.get("/articles")
def list_articles(
    keyword: str | None = None,
    category: str | None = None,
    analyzed: bool | None = None,
    min_importance: int | None = Query(
        default=None,
        ge=1,
        le=5,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
):
    return get_articles(
        keyword=keyword,
        category=category,
        min_importance=min_importance,
        analyzed=analyzed,
        limit=limit,
        offset=offset,
    )

@app.post("/articles")
def add_article(article: ArticleCreate):
    return create_article(
        article.title,
        article.category,
        article.importance,
    )

@app.get("/articles/{article_id}")
def get_one_article(article_id: int):
    article = get_article(article_id)

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="文章不存在",
        )

    return article

@app.put("/articles/{article_id}")
def edit_article(article_id: int, article: ArticleCreate):
    updated_article = update_article(
        article_id,
        article.title,
        article.category,
        article.importance,

    )

    if updated_article is None:
        raise HTTPException(
            status_code=404,
            detail="文章不存在",
        )

    return updated_article

@app.delete("/articles/{article_id}")
def remove_article(article_id: int):
    deleted = delete_article(article_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="文章不存在",
        )

    return {
        "message": "文章删除成功",
        "id": article_id,
    }

@app.get("/stats")
def statistics():
    return get_statistics()

@app.post("/articles/{article_id}/analyze")
def analyze_one_article(article_id: int):
    logger.info("开始分析文章 article_id=%s", article_id)
    article = get_article(article_id)

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="文章不存在",
        )

    try:
        analysis = analyze_article(article)
        save_analysis(article_id, analysis)
        logger.info("分析结果已保存 article_id=%s", article_id)
    except Exception as error:
        logger.exception("文章分析失败 article_id=%s", article_id)
        raise HTTPException(
            status_code=502,
            detail=f"DeepSeek 分析失败：{error}",
        )

    return {
        "article": article,
        "analysis": analysis,
    }

@app.post("/sources/dev/import")
def import_dev_articles(
    tag: str = "ai",
    limit: int = Query(default=5, ge=1, le=20),
):
    raw_articles = fetch_dev_articles(
        tag=tag,
        limit=limit,
    )

    articles = normalize_dev_articles(raw_articles)
    imported_articles = []
    skipped_articles = []

    for article in articles:
        existing_article = get_article_by_title(
            article["title"]
        )

        if existing_article is not None:
            skipped_articles.append(existing_article)
            continue

        saved_article = create_article(
            article["title"],
            article["category"],
            article["importance"],
        )

        imported_articles.append(saved_article)

    logger.info(
        "DEV 文章导入完成 count=%s",
        len(imported_articles),
    )

    return {
        "source": "DEV",
        "tag": tag,
        "fetched": len(raw_articles),
        "imported": len(imported_articles),
        "skipped": len(skipped_articles),
        "articles": imported_articles,
    }

@app.post("/analysis/batch")
def analyze_all_articles(
    limit: int = Query(
            default=5,
            ge=1,
            le=20,
        )
    ):
    articles = get_articles(limit=limit)

    logger.info(
        "批量分析开始 total=%s limit=%s",
        len(articles),
        limit,
    )

    batch_status["status"] = "running"
    batch_status["started_at"] = datetime.now().isoformat()
    batch_status["finished_at"] = None
    batch_status["total"] = len(articles)
    batch_status["completed"] = 0
    batch_status["failed"] = 0
    results = []
    failures = []

    for article in articles:
        existing_analysis = get_analysis(article["id"])

        if existing_analysis is not None:
            results.append({
                "article_id": article["id"],
                "title": article["title"],
                "status": "skipped",
                "analysis": existing_analysis,
            })
            batch_status["completed"] += 1
            continue

        try:
            analysis = analyze_article(article)
            save_analysis(article["id"], analysis)

            results.append({
                "article_id": article["id"],
                "title": article["title"],
                "status": "analyzed",
                "analysis": analysis,
            })
            batch_status["completed"] += 1

        except Exception as error:
            failures.append({
                "article_id": article["id"],
                "title": article["title"],
                "error": str(error),
            })
            batch_status["failed"] += 1

    batch_status["status"] = "completed"
    batch_status["finished_at"] = datetime.now().isoformat()
    logger.info(
        "批量分析完成 total=%s completed=%s failed=%s",
        batch_status["total"],
        batch_status["completed"],
        batch_status["failed"],
    )

    return {
        "total": len(articles),
        "analyzed": sum(
            item["status"] == "analyzed" for item in results
        ),
        "skipped": sum(
            item["status"] == "skipped" for item in results
        ),
        "failed": len(failures),
        "results": results,
        "failures": failures,
    }

@app.get("/analysis/batch/status")
def get_batch_status():
    return batch_status

@app.get("/articles/{article_id}/analysis")
def get_saved_analysis(article_id: int):
    analysis = get_analysis(article_id)

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="这篇文章还没有分析结果",
        )

    return analysis

@app.get("/health")
def health_check():
    try:
        get_statistics()

        return {
            "status": "ok",
            "database": "ok",
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"服务异常：{error}",
        )