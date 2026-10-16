from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

DOCS = """MITRE ATT&CK T1059: Command and Scripting Interpreter

Adversaries abuse PowerShell and command shells to execute arbitrary commands.

---

MITRE ATT&CK T1486: Data Encrypted for Impact

Adversaries encrypt files to interrupt availability, typical of ransomware."""


@pytest.fixture
def client(monkeypatch, tmp_path):
    docs = tmp_path / "docs.txt"
    docs.write_text(DOCS, encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("DOCS_PATH", str(docs))

    # 重新載入設定，並同步到已經 import 過它的模組
    import app.config as config
    config.settings = config.Settings()

    import app.service as service
    import app.main as main
    service.settings = config.settings
    main.settings = config.settings

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Summary\nThreat mapping\nDefense")]

    with patch("app.service.Anthropic") as mock_cls:
        mock_create = mock_cls.return_value.messages.create
        mock_create.return_value = mock_message
        with TestClient(main.app) as test_client:
            test_client.mock_create = mock_create
            yield test_client


def test_health_reports_loaded_documents(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "documents_loaded": 2}


def test_short_question_is_rejected_by_validation(client):
    response = client.post("/ask", json={"question": "hi"})
    assert response.status_code == 422
    assert client.mock_create.call_count == 0


def test_irrelevant_question_returns_no_match_without_calling_llm(client):
    response = client.post(
        "/ask", json={"question": "banana bread pudding recipe"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sources"] == []
    assert "No relevant information" in body["answer"]
    assert client.mock_create.call_count == 0


def test_relevant_question_returns_answer_with_sources(client):
    response = client.post(
        "/ask", json={"question": "how do attackers abuse powershell"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"].startswith("Summary")
    assert len(body["sources"]) >= 1
    assert body["sources"][0]["score"] > 0
    assert body["latency_ms"] >= 0
    assert client.mock_create.call_count == 1
