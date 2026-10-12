import logging
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

_embeddings = None


def get_embedder(model_name: str) -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embedding model via LangChain: {model_name}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def get_embeddings(texts: list[str], model_name: str) -> list[list[float]]:
    if not texts:
        return []
    embedder = get_embedder(model_name)
    return embedder.embed_documents(texts)
