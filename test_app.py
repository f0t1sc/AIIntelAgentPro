from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "AIIntelAgent Pro is running"


def test_list_articles():
    response = client.get("/articles")

    assert response.status_code == 200

    articles = response.json()
    assert isinstance(articles, list)

    if articles:
        assert "id" in articles[0]
        assert "title" in articles[0]
        assert "analyzed" in articles[0]


def test_filter_analyzed_articles():
    response = client.get("/articles?analyzed=true")

    assert response.status_code == 200

    for article in response.json():
        assert article["analyzed"] == 1

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"


def test_filter_unanalyzed_articles():
    response = client.get("/articles?analyzed=false")

    assert response.status_code == 200

    for article in response.json():
        assert article["analyzed"] == 0

def test_get_missing_article():
    response = client.get("/articles/999999")

    assert response.status_code == 404

def test_get_missing_analysis():
    response = client.get("/articles/999999/analysis")

    assert response.status_code == 404