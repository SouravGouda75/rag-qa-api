import logging
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.core.retriever import retrieve
from app.core.answerer import answer_question
from app.models.schemas import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if len(question) > settings.max_question_length:
        raise HTTPException(
            status_code=400,
            detail=f"Question exceeds maximum length of {settings.max_question_length} characters",
        )

    top_k = request.top_k or settings.top_k
    chunks = retrieve(question, top_k=top_k)
    return answer_question(question, chunks)
