from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_anonymize_ok():
    payload = {
        "text": "Contact me at test@example.com tomorrow.",
        "entity_types": ["EMAIL", "DATE"],
    }
    res = client.post("/api/anonymize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "anonymized_text" in data
    assert "meta" in data

