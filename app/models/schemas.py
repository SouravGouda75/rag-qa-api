from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    document_name: str
    num_chunks: int
    status: str
    language: str = "en"
    warnings: list[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    source_document: str = Field(..., description="Source document filename")
    excerpt: str = Field(..., description="Verbatim text snippet pulled from source")


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class GroundedAnswer(BaseModel):
    answer: str = Field(..., description="Answer grounded strictly in provided context")
    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="Verbatim text snippets and source document names",
    )


class QueryResponse(BaseModel):
    answer: str
    evidence: list[EvidenceItem] = Field(default_factory=list)


class RetrievedChunk(BaseModel):
    text: str
    document: str
    chunk_index: int
    score: float = 0.0


class HealthResponse(BaseModel):
    status: str
    documents_count: int = 0
    chunks_count: int = 0
