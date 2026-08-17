import httpx


DEV_ARTICLES_URL = "https://dev.to/api/articles"

HEADERS = {
    "Accept": "application/vnd.forem.api-v1+json",
    "User-Agent": "AIIntelAgentPro/1.0",
}


def fetch_dev_articles(tag="ai", limit=5):
    response = httpx.get(
        DEV_ARTICLES_URL,
        params={
            "tag": tag,
            "per_page": limit,
        },
        headers=HEADERS,
        timeout=10.0,
    )

    response.raise_for_status()

    articles = response.json()

    if not isinstance(articles, list):
        raise ValueError("DEV API 返回的数据不是列表")

    return articles


def normalize_dev_articles(raw_articles):
    normalized_articles = []

    for article in raw_articles:
        title = article.get("title", "").strip()

        user = article.get("user") or {}
        author = user.get("name", "Unknown").strip()

        if not title:
            continue

        normalized_articles.append({
            "title": title,
            "category": f"DEV/{author}",
            "importance": 3,
        })

    return normalized_articles