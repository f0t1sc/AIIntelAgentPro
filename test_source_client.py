from source_client import normalize_dev_articles


def test_normalize_dev_articles():
    raw_articles = [
        {
            "title": "  AI Agents in Business  ",
            "user": {
                "name": "Alice",
            },
        },
        {
            "title": "",
            "user": {
                "name": "Bob",
            },
        },
    ]

    result = normalize_dev_articles(raw_articles)

    assert len(result) == 1
    assert result[0]["title"] == "AI Agents in Business"
    assert result[0]["category"] == "DEV/Alice"
    assert result[0]["importance"] == 3