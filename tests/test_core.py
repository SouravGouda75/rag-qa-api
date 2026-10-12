import pytest
from app.core.chunker import chunk_text, get_chunk_params, estimate_density
from app.core.parser import parse_file, SUPPORTED_EXTENSIONS


class TestParser:
    def test_supported_extensions(self):
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".txt" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS

    def test_parse_txt_utf8(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Hello world. This is a test document.", encoding="utf-8")
        result = parse_file(str(f))
        assert "Hello world" in result

    def test_parse_txt_latin1_encoding(self, tmp_path):
        f = tmp_path / "latin1.txt"
        f.write_bytes("Café résumé señorita".encode("latin-1"))
        result = parse_file(str(f))
        assert "Café" in result or "résumé" in result

    def test_parse_empty_file_raises_error(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="empty"):
            parse_file(str(f))

    def test_file_size_exceeded_raises_error(self, tmp_path):
        f = tmp_path / "large.txt"
        f.write_text("sample content", encoding="utf-8")
        with pytest.raises(ValueError, match="exceeds limit"):
            parse_file(str(f), max_size_mb=0)

    def test_parse_md(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Title\n\nSome **bold** text and a [link](http://example.com).", encoding="utf-8")
        result = parse_file(str(f))
        assert "Title" in result
        assert "bold" in result
        assert "<" not in result

    def test_unsupported_extension(self, tmp_path):
        f = tmp_path / "test.xyz"
        f.write_text("content", encoding="utf-8")
        with pytest.raises(ValueError, match="Unsupported"):
            parse_file(str(f))


class TestChunker:
    def test_basic_chunking(self):
        text = "A" * 1000
        chunks = chunk_text(text, "test.txt", chunk_size=200, overlap=0)
        assert len(chunks) >= 5
        assert all(c.document == "test.txt" for c in chunks)

    def test_chunk_metadata(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = chunk_text(text, "doc.md", chunk_size=500, overlap=0)
        assert chunks[0].document == "doc.md"
        assert chunks[0].chunk_index == 0

    def test_empty_text(self):
        chunks = chunk_text("", "empty.txt", chunk_size=500, overlap=0)
        assert len(chunks) == 0

    def test_whitespace_only_text(self):
        chunks = chunk_text("   \n\n   \t  ", "blank.txt")
        assert len(chunks) == 0

    def test_overlap_produces_content(self):
        text = "Word " * 200
        chunks = chunk_text(text, "test.txt", chunk_size=100, overlap=20)
        assert len(chunks) > 1

    def test_short_text_single_chunk(self):
        text = "Short text."
        chunks = chunk_text(text, "short.txt", chunk_size=500, overlap=50)
        assert len(chunks) == 1
        assert chunks[0].text == "Short text."

    def test_adaptive_chunking_density_estimation(self):
        dense_text = "Rule 1. Fact A. Code 42. Date 1999. Term 5."
        narrative_text = "In an extraordinarily serene landscape that stretched as far as the human eye could see, ancient mountains stood like silent sentinels guarding secrets long forgotten by time and generations past."
        assert estimate_density(dense_text) == "dense"
        assert estimate_density(narrative_text) == "narrative"

    def test_adaptive_chunk_size_variation(self):
        dense_text = "Rule 1. Fact A. Code 42. Date 1999."
        dense_size, _ = get_chunk_params("rules.txt", dense_text, adaptive=True, base_chunk_size=500)
        narrative_size, _ = get_chunk_params("story.md", "Long flowing text without many breaks " * 10, adaptive=True, base_chunk_size=500)
        assert dense_size < narrative_size
