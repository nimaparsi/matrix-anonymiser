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


def test_anonymize_reverses_pronouns_when_requested():
    payload = {
        "text": "You can reach him at test@example.com. His notebook is ready.",
        "entity_types": ["EMAIL"],
        "reverse_pronouns": True,
    }
    res = client.post("/api/anonymize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["anonymized_text"] == "You can reach her at [EMAIL_1]. Her notebook is ready."
    assert data["meta"]["reverse_pronouns"] is True


def test_anonymize_handles_possessive_her_during_pronoun_reversal():
    payload = {
        "text": "You can reach her at test@example.com or on her mobile 1234567890.",
        "entity_types": ["EMAIL", "PHONE"],
        "reverse_pronouns": True,
    }
    res = client.post("/api/anonymize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["anonymized_text"] == "You can reach him at [EMAIL_1] or on his mobile [PHONE_1]."


def test_anonymize_accepts_reverse_pronouns_camel_case():
    payload = {
        "text": "She confirmed he will send the report.",
        "entity_types": ["PERSON"],
        "reversePronouns": True,
    }
    res = client.post("/api/anonymize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["anonymized_text"] == "He confirmed she will send the report."
    assert data["meta"]["reversePronouns"] is True


def test_anonymize_skips_pronoun_reversal_for_non_english_text():
    payload = {
        "text": "Hola, her email es test@example.com.",
        "entity_types": ["EMAIL"],
        "reverse_pronouns": True,
    }
    res = client.post("/api/anonymize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["anonymized_text"] == "Hola, her email es [EMAIL_1]."
