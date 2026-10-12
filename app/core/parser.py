import logging
import re
from pathlib import Path
import chardet
from pypdf import PdfReader
import markdown

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text and text.strip():
            pages.append(text.strip())

    if not pages:
        raise ValueError("PDF contains no extractable text")

    return "\n\n".join(pages)


def _decode_bytes(raw_bytes: bytes) -> str:
    if not raw_bytes:
        raise ValueError("File is empty")

    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        pass

    detected = chardet.detect(raw_bytes)
    encoding = detected.get("encoding") or "latin-1"

    try:
        return raw_bytes.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        return raw_bytes.decode("latin-1", errors="replace")


def parse_txt(file_path: str) -> str:
    raw_bytes = Path(file_path).read_bytes()
    return _decode_bytes(raw_bytes)


def parse_markdown(file_path: str) -> str:
    raw_bytes = Path(file_path).read_bytes()
    raw = _decode_bytes(raw_bytes)
    html = markdown.markdown(raw)
    clean = re.sub(r"<[^>]+>", "", html)
    return clean


PARSERS = {
    ".pdf": parse_pdf,
    ".txt": parse_txt,
    ".md": parse_markdown,
}

SUPPORTED_EXTENSIONS = set(PARSERS.keys())


def validate_file_size(file_path: str, max_size_mb: int) -> None:
    size_bytes = Path(file_path).stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"File size ({size_mb:.1f}MB) exceeds limit ({max_size_mb}MB)")


def parse_file(file_path: str, max_size_mb: int = 50) -> str:
    ext = Path(file_path).suffix.lower()
    if ext not in PARSERS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}")

    validate_file_size(file_path, max_size_mb)
    return PARSERS[ext](file_path)
