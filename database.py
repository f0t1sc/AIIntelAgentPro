import sqlite3
import json
from pathlib import Path


DATABASE_FILE = Path(__file__).parent / "articles.db"


def initialize_database():
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                importance INTEGER NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS article_analysis (
                article_id INTEGER PRIMARY KEY,
                summary TEXT NOT NULL,
                category TEXT NOT NULL,
                importance INTEGER NOT NULL,
                keywords TEXT NOT NULL,
                analyzed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        count = connection.execute(
            "SELECT COUNT(*) FROM articles"
        ).fetchone()[0]

        if count == 0:
            connection.executemany(
                """
                INSERT INTO articles (title, category, importance)
                VALUES (?, ?, ?)
                """,
                [
                    ("AI Agent 开始进入企业工作流", "Agent应用", 4),
                    ("OpenAI 发布新模型", "AI模型", 5),
                    ("如何优化 LLM 上下文", "技术优化", 4),
                ],
            )


def get_articles(
    keyword=None,
    category=None,
    min_importance=None,
    analyzed=None,
    limit=20,
    offset=0,
):
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.row_factory = sqlite3.Row

        sql = """
              SELECT articles.id, \
                     articles.title, \
                     articles.category, \
                     articles.importance, \
                     CASE \
                         WHEN article_analysis.article_id IS NULL THEN 0 \
                         ELSE 1 \
                     END AS analyzed
              FROM articles
              LEFT JOIN article_analysis
                  ON articles.id = article_analysis.article_id
              WHERE 1 = 1 \
        """
        params = []

        if keyword:
            sql += " AND articles.title LIKE ?"
            params.append(f"%{keyword}%")

        if category:
            sql += " AND articles.category = ?"
            params.append(category)

        if min_importance is not None:
            sql += " AND articles.importance >= ?"
            params.append(min_importance)

        if analyzed is True:
            sql += " AND article_analysis.article_id IS NOT NULL"

        elif analyzed is False:
            sql += " AND article_analysis.article_id IS NULL"

        sql += """
            ORDER BY articles.importance DESC, articles.id DESC
            LIMIT ? OFFSET ?
        """

        params.extend([limit, offset])

        rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

def create_article(title, category, importance):
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.execute(
            """
            INSERT INTO articles (title, category, importance)
            VALUES (?, ?, ?)
            """,
            (title, category, importance),
        )

        return {
            "id": cursor.lastrowid,
            "title": title,
            "category": category,
            "importance": importance,
        }

def get_article(article_id):
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT id, title, category, importance
            FROM articles
            WHERE id = ?
            """,
            (article_id,),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

def update_article(article_id, title, category, importance):
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute(
            """
            UPDATE articles
            SET title = ?, category = ?, importance = ?
            WHERE id = ?
            """,
            (title, category, importance, article_id),
        )

        if cursor.rowcount == 0:
            return None

        row = connection.execute(
            """
            SELECT id, title, category, importance
            FROM articles
            WHERE id = ?
            """,
            (article_id,),
        ).fetchone()

        return dict(row)

def delete_article(article_id):
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.execute(
            """
            DELETE FROM articles
            WHERE id = ?
            """,
            (article_id,),
        )

        return cursor.rowcount > 0

def get_statistics():
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.row_factory = sqlite3.Row
        total = connection.execute(
            """
            SELECT COUNT(*)
            FROM articles
            """
        ).fetchone()[0]

        average_importance = connection.execute(
            """
            SELECT AVG(importance)
            FROM articles
            """
        ).fetchone()[0]

        category_rows = connection.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM articles
            GROUP BY category
            ORDER BY count DESC
            """
        ).fetchall()

        return {
            "total": total,
            "average_importance": round(average_importance or 0, 2),
            "categories": [
                {
                    "category": row["category"],
                    "count": row["count"],
                }
                for row in category_rows
            ],
        }

def save_analysis(article_id, analysis):
    analysis_data = analysis.model_dump()

    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            INSERT INTO article_analysis (
                article_id,
                summary,
                category,
                importance,
                keywords
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(article_id) DO UPDATE SET
                summary = excluded.summary,
                category = excluded.category,
                importance = excluded.importance,
                keywords = excluded.keywords,
                analyzed_at = CURRENT_TIMESTAMP
            """,
            (
                article_id,
                analysis_data["summary"],
                analysis_data["category"],
                analysis_data["importance"],
                json.dumps(
                    analysis_data["keywords"],
                    ensure_ascii=False,
                ),
            ),
        )

def get_analysis(article_id):
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT
                article_id,
                summary,
                category,
                importance,
                keywords,
                analyzed_at
            FROM article_analysis
            WHERE article_id = ?
            """,
            (article_id,),
        ).fetchone()

        if row is None:
            return None

        result = dict(row)
        result["keywords"] = json.loads(result["keywords"])

        return result