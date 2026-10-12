import uuid
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, HTTPException
from langdetect import detect, LangDetectException

from app.config import settings
from app.core.parser import parse_file, SUPPORTED_EXTENSIONS
from app.core.chunker import chunk_text
from app.core.retriever import store_chunks, document_exists, delete_document
from app.models.schemas import IngestResponse

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)


def _detect_language(text: str) -> tuple[str, list[str]]:
    warnings = []
    try:
        lang = detect(text[:5000])
    except LangDetectException:
        return "unknown", ["Could not detect document language"]

    if lang not in settings.supported_languages:
        warnings.append(
            f"Document language detected as '{lang}'. "
            f"Embedding model is optimized for {', '.join(settings.supported_languages)}. "
            f"Retrieval quality may be degraded."
        )

    return lang, warnings


def _sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = "".join(c if c.isalnum() or c in "._- " else "_" for c in name)
    return name.strip() or "unnamed_document"


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    filename = _sanitize_filename(file.filename)
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")

    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({size_mb:.1f}MB) exceeds the {settings.max_file_size_mb}MB limit",
        )

    save_path = UPLOAD_DIR / filename
    save_path.write_bytes(content)

    warnings = []

    try:
        text = parse_file(
            str(save_path),
            max_size_mb=settings.max_file_size_mb,
        )
    except ValueError as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        logger.error(f"Unexpected parse error for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {e}")

    if not text.strip():
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="File contains no extractable text")

    lang, lang_warnings = _detect_language(text)
    warnings.extend(lang_warnings)

    if document_exists(filename):
        deleted_count = delete_document(filename)
        warnings.append(f"Document '{filename}' already existed. Replaced {deleted_count} previous chunks.")
        logger.info(f"Replaced existing document: {filename} ({deleted_count} chunks)")

    chunks = chunk_text(
        text,
        document_name=filename,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
        adaptive=settings.adaptive_chunking,
    )

    if not chunks:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Document produced no usable chunks after processing")

    doc_id = uuid.uuid4().hex[:8]
    ids = [f"{doc_id}_chunk_{c.chunk_index}" for c in chunks]
    metadatas = [{"document": c.document, "chunk_index": c.chunk_index} for c in chunks]
    texts = [c.text for c in chunks]

    try:
        store_chunks(texts, metadatas, ids)
    except Exception as e:
        save_path.unlink(missing_ok=True)
        logger.error(f"Failed to store chunks for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store document in vector database: {e}")

    return IngestResponse(
        document_name=filename,
        num_chunks=len(chunks),
        status="ingested",
        language=lang,
        warnings=warnings,
    )
