import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

class ArticleAnalysis(BaseModel):
    summary: str = Field(min_length=1)
    category: str = Field(min_length=1)
    importance: int = Field(ge=1, le=5)
    keywords: list[str] = Field(min_length=1)

def analyze_article(article):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        raise RuntimeError("没有找到 DEEPSEEK_API_KEY")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=30.0,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是AI资讯分析助手。"
                    "请只返回合法JSON，字段包括summary、category、"
                    "importance和keywords。"
                ),
            },
            {
                "role": "user",
                "content": json.dumps(article, ensure_ascii=False),
            },
        ],
        response_format={"type": "json_object"},
        extra_body={
            "thinking": {
                "type": "disabled"
            }
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("模型没有返回内容")

    return ArticleAnalysis.model_validate_json(content)