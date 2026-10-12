from unittest.mock import patch, MagicMock
from app.models.schemas import EvidenceItem, QueryResponse


class TestQueryEndpoint:
    def test_query_returns_structured_response(self, client):
        mock_response = QueryResponse(
            answer="test answer",
            evidence=[EvidenceItem(source_document="doc.txt", excerpt="test excerpt")],
        )

        with patch("app.api.query.retrieve") as mock_retrieve, \
             patch("app.api.query.answer_question", return_value=mock_response):
            mock_retrieve.return_value = []
            response = client.post("/query", json={"question": "test question"})

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "test answer"
        assert "evidence" in data
        assert len(data["evidence"]) == 1
        assert data["evidence"][0]["source_document"] == "doc.txt"
        assert data["evidence"][0]["excerpt"] == "test excerpt"

    def test_query_with_custom_top_k(self, client):
        mock_response = QueryResponse(
            answer="answer",
            evidence=[],
        )

        with patch("app.api.query.retrieve") as mock_retrieve, \
             patch("app.api.query.answer_question", return_value=mock_response):
            mock_retrieve.return_value = []
            response = client.post("/query", json={"question": "test", "top_k": 3})

        assert response.status_code == 200
        mock_retrieve.assert_called_once_with("test", top_k=3)

    def test_query_empty_question(self, client):
        response = client.post("/query", json={"question": "   "})
        assert response.status_code in (400, 422)

    def test_query_oversized_question(self, client):
        long_q = "what is " + ("x" * 2500)
        response = client.post("/query", json={"question": long_q})
        assert response.status_code in (400, 422)

    def test_health_endpoint_returns_stats(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "documents_count" in data
        assert "chunks_count" in data
