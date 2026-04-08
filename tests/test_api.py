"""
Integration tests for KayakFlow AI API.
Run with: pytest tests/ -v
"""
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

os.environ.setdefault("GROQ_API_KEY", "test-key-placeholder")

from main import app  # noqa: E402

client = TestClient(app)


def test_health_check():
    """Health endpoint must return 200 and ok status."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "ts" in data


def test_serve_ui_exists():
    """Root should serve index.html (200) or 404 if missing."""
    res = client.get("/")
    assert res.status_code in (200, 404)


def test_history_empty():
    """History endpoint returns a list."""
    res = client.get("/api/v1/history")
    assert res.status_code == 200
    assert "items" in res.json()


def test_generate_missing_key():
    """Empty input should not crash the server."""
    res = client.post("/api/v1/generate", json={"user_input": ""})
    # Either 200 (LLM response) or 422 (validation) — never 500
    assert res.status_code in (200, 422)


@patch("services.client")
@patch("services.generate_marketing_image", return_value="latest_promo.png")
def test_generate_mocked(mock_img, mock_groq_client):
    """Mocked LLM call should return complete status."""
    mock_choice = MagicMock()
    mock_choice.choices[0].message.content = '''{
        "status": "complete",
        "tour_title": "Sunset Kayak",
        "platforms": {"instagram": "Amazing tour!", "whatsapp": "Book now!"},
        "hashtags": ["berlin", "kayak"],
        "image_prompt": "kayak at sunset",
        "email_subject": ""
    }'''
    mock_groq_client.chat.completions.create.return_value = mock_choice

    res = client.post("/api/v1/generate", json={
        "user_input": "Sunset kayak for couples",
        "tone": "romantic",
        "platforms": ["instagram", "whatsapp"],
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "complete"
    assert "content" in data


def test_delete_nonexistent_history():
    """Deleting a non-existent ID should return 404."""
    res = client.delete("/api/v1/history/nonexistent-id-12345")
    assert res.status_code == 404
