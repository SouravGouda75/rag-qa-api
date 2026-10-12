from pathlib import Path
from unittest.mock import patch

SAMPLE_DIR = Path(__file__).parent.parent / "sample_docs"


class TestIngestEndpoint:
    def test_ingest_txt_file(self, client):
        file_path = SAMPLE_DIR / "company_policy.txt"
        with open(file_path, "rb") as f:
            response = client.post("/ingest", files={"file": ("company_policy.txt", f)})
        assert response.status_code == 200
        data = response.json()
        assert data["document_name"] == "company_policy.txt"
        assert data["num_chunks"] > 0
        assert data["status"] == "ingested"
        assert data["language"] == "en"

    def test_ingest_md_file(self, client):
        file_path = SAMPLE_DIR / "python_basics.md"
        with open(file_path, "rb") as f:
            response = client.post("/ingest", files={"file": ("python_basics.md", f)})
        assert response.status_code == 200
        data = response.json()
        assert data["num_chunks"] > 0

    def test_duplicate_document_replaces_old(self, client):
        file_path = SAMPLE_DIR / "company_policy.txt"
        with open(file_path, "rb") as f:
            resp1 = client.post("/ingest", files={"file": ("company_policy.txt", f)})
        assert resp1.status_code == 200

        with open(file_path, "rb") as f:
            resp2 = client.post("/ingest", files={"file": ("company_policy.txt", f)})
        assert resp2.status_code == 200
        data = resp2.json()
        assert any("already existed" in w for w in data["warnings"])

    def test_non_english_warning(self, client):
        spanish_text = (
            "Este es un documento redactado enteramente en el idioma español. "
            "El objetivo es verificar que el sistema de detección lingüística "
            "genere una advertencia explícita sobre el modelo de incrustación."
        )
        response = client.post(
            "/ingest",
            files={"file": ("spanish_doc.txt", spanish_text.encode("utf-8"))},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "es"
        assert any("optimized for" in w for w in data["warnings"])

    def test_ingest_unsupported_file(self, client):
        response = client.post(
            "/ingest",
            files={"file": ("data.csv", b"col1,col2\nval1,val2")},
        )
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]

    def test_ingest_empty_file(self, client):
        response = client.post(
            "/ingest",
            files={"file": ("empty.txt", b"")},
        )
        assert response.status_code == 422

    def test_ingest_oversized_file(self, client):
        with patch("app.api.ingest.settings.max_file_size_mb", 0.0001):
            response = client.post(
                "/ingest",
                files={"file": ("large.txt", b"A" * 500)},
            )
            assert response.status_code == 413
            assert "exceeds" in response.json()["detail"]
