import os
import shutil
import pytest
from fastapi.testclient import TestClient

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["CHROMA_PERSIST_DIR"] = "./test_chroma_data"
os.environ["ENABLE_RERANKING"] = "false"

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True, scope="session")
def cleanup():
    yield
    for path in ["./test_chroma_data", "./uploaded_docs"]:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
