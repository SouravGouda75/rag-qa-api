import logging
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import settings
from app.core.embedder import get_embedder
from app.models.schemas import RetrievedChunk

logger = logging.getLogger(__name__)

_vectorstore = None


def _get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        embedder = get_embedder(settings.embedding_model)
        _vectorstore = Chroma(
            collection_name="documents",
            embedding_function=embedder,
            persist_directory=settings.chroma_persist_dir,
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _vectorstore


def document_exists(document_name: str) -> bool:
    vs = _get_vectorstore()
    if vs._collection.count() == 0:
        return False
    results = vs.get(where={"document": document_name}, limit=1)
    return bool(results and results.get("ids"))


def delete_document(document_name: str) -> int:
    vs = _get_vectorstore()
    if vs._collection.count() == 0:
        return 0
    results = vs.get(where={"document": document_name})
    ids = results.get("ids", [])
    if ids:
        vs.delete(ids=ids)
        return len(ids)
    return 0


def store_chunks(chunks_text: list[str], metadatas: list[dict], ids: list[str]):
    vs = _get_vectorstore()
    docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(chunks_text, metadatas)
    ]
    batch_size = 5000
    for i in range(0, len(ids), batch_size):
        end = i + batch_size
        vs.add_documents(documents=docs[i:end], ids=ids[i:end])


def get_collection_stats() -> dict:
    global _vectorstore
    if _vectorstore is None:
        return {"chunks_count": 0, "documents_count": 0}
    try:
        count = _vectorstore._collection.count()
        if count == 0:
            return {"chunks_count": 0, "documents_count": 0}

        all_meta = _vectorstore.get(include=["metadatas"])
        doc_names = {m.get("document") for m in all_meta.get("metadatas", []) if m}
        return {"chunks_count": count, "documents_count": len(doc_names)}
    except Exception:
        return {"chunks_count": 0, "documents_count": 0}


SUMMARY_KEYWORDS = [
    "summarize", "summary", "overview", "tl;dr", "tldr",
    "main points", "about the document", "content of the pdf",
    "content of the document", "core findings", "what is this document about"
]


def _is_summary_query(query: str) -> bool:
    q = query.strip().lower()
    return any(k in q for k in SUMMARY_KEYWORDS)


def _get_lead_chunks(vs, count: int = 2) -> list[RetrievedChunk]:
    try:
        lead_data = vs.get(where={"chunk_index": {"$lte": count - 1}}, limit=count)
        if not lead_data or not lead_data.get("documents"):
            return []

        lead_chunks = []
        for text, meta in zip(lead_data["documents"], lead_data["metadatas"]):
            lead_chunks.append(RetrievedChunk(
                text=text,
                document=meta.get("document", "document"),
                chunk_index=meta.get("chunk_index", 0),
                score=1.0,
            ))
        return lead_chunks
    except Exception as e:
        logger.warning(f"Failed to fetch lead chunks: {e}")
        return []


def retrieve(query: str, top_k: int = 5) -> list[RetrievedChunk]:
    vs = _get_vectorstore()
    total_docs = vs._collection.count()
    if total_docs == 0:
        return []

    fetch_k = min(top_k, total_docs)
    results = vs.similarity_search_with_score(query, k=fetch_k)

    chunks = []
    for doc, distance in results:
        meta = doc.metadata or {}
        similarity = round(1.0 - float(distance), 4) if distance is not None else 0.0
        chunks.append(RetrievedChunk(
            text=doc.page_content,
            document=meta.get("document", "unknown"),
            chunk_index=meta.get("chunk_index", 0),
            score=similarity,
        ))

    # Prioritize lead chunks for summary / global overview queries
    if _is_summary_query(query):
        leads = _get_lead_chunks(vs, count=2)
        existing_texts = {c.text for c in chunks}
        augmented = [l for l in leads if l.text not in existing_texts] + chunks
        return augmented[:top_k]

    return chunks


def reset_collection():
    global _vectorstore
    if _vectorstore is not None:
        try:
            _vectorstore.delete_collection()
        except Exception:
            pass
        _vectorstore = None
