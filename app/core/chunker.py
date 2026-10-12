import re
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    text: str
    document: str
    chunk_index: int


CHUNK_PROFILES = {
    ".txt": {"chunk_size": 400, "overlap": 60},
    ".md":  {"chunk_size": 600, "overlap": 80},
    ".pdf": {"chunk_size": 500, "overlap": 50},
}

DEFAULT_PROFILE = {"chunk_size": 500, "overlap": 50}


def estimate_density(text: str) -> str:
    raw_sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    if not sentences:
        return "standard"

    avg_sentence_len = sum(len(s) for s in sentences) / len(sentences)

    if avg_sentence_len < 60:
        return "dense"
    elif avg_sentence_len > 120:
        return "narrative"
    return "standard"


DENSITY_MULTIPLIERS = {
    "dense": 0.7,
    "standard": 1.0,
    "narrative": 1.4,
}


def get_chunk_params(
    document_name: str,
    text: str,
    adaptive: bool = True,
    base_chunk_size: int = 500,
    base_overlap: int = 50,
) -> tuple[int, int]:
    if not adaptive:
        return base_chunk_size, base_overlap

    ext = "." + document_name.rsplit(".", 1)[-1].lower() if "." in document_name else ""
    profile = CHUNK_PROFILES.get(ext, DEFAULT_PROFILE)

    density = estimate_density(text)
    multiplier = DENSITY_MULTIPLIERS[density]

    chunk_size = max(100, int(profile["chunk_size"] * multiplier))
    overlap = max(20, int(profile["overlap"] * multiplier))
    overlap = min(overlap, chunk_size // 4)

    return chunk_size, overlap


def chunk_text(
    text: str,
    document_name: str,
    chunk_size: int = 500,
    overlap: int = 50,
    adaptive: bool = False,
) -> list[Chunk]:
    if not text or not text.strip():
        return []

    if adaptive:
        chunk_size, overlap = get_chunk_params(document_name, text, adaptive, chunk_size, overlap)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        strip_whitespace=True,
    )

    raw_chunks = splitter.split_text(text)
    chunks = [c.strip() for c in raw_chunks if c.strip()]

    return [
        Chunk(text=chunk_str, document=document_name, chunk_index=i)
        for i, chunk_str in enumerate(chunks)
    ]
