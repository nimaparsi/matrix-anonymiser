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
    assert data["warning"] is None
    assert data["meta"]["detected_language"] == "en"


def test_anonymize_returns_warning_for_non_english_text():
    payload = {
        "text": "Hola, me llamo Carlos y vivo en Madrid. Mi correo es carlos@example.com.",
        "entity_types": ["PERSON", "EMAIL"],
    }
    res = client.post("/api/anonymize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["anonymized_text"]
    assert data["warning"] == "This text appears to be non-English. Entity detection may be less accurate."
    assert data["meta"]["supported_language"] == "English"
    assert data["meta"]["detected_language"] == "es"
