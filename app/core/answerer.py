import logging
from pathlib import Path
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.config import settings
from app.models.schemas import RetrievedChunk, QueryResponse, GroundedAnswer, EvidenceItem

logger = logging.getLogger(__name__)

PROMPT_FILE = Path(__file__).resolve().parent.parent.parent / "prompts" / "qa_prompt.yml"


def _load_prompt_config() -> dict:
    if PROMPT_FILE.exists():
        try:
            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            logger.warning(f"Failed to read prompt file {PROMPT_FILE}: {e}")

    return {
        "system_prompt": (
            "You are a factual assistant that answers questions using ONLY the provided context.\n\n"
            "Rules:\n"
            "1. Answer based strictly on the context below. Do not use outside knowledge or make assumptions.\n"
            "2. If the context does not contain enough information to answer, state: "
            "\"The provided documents do not contain information to answer this question.\" and leave evidence empty.\n"
            "3. Include relevant verbatim excerpts in evidence with their source_document filename.\n"
        ),
        "human_prompt": "Context:\n{context}\n\nQuestion: {question}",
        "refusal_message": "The provided documents do not contain information to answer this question.",
    }


_PROMPT_CONFIG = _load_prompt_config()
SYSTEM_PROMPT = _PROMPT_CONFIG["system_prompt"]
HUMAN_PROMPT = _PROMPT_CONFIG.get("human_prompt", "Context:\n{context}\n\nQuestion: {question}")
REFUSAL_MESSAGE = _PROMPT_CONFIG.get(
    "refusal_message",
    "The provided documents do not contain information to answer this question.",
)

_chat_model = None
_structured_llm = None


def _get_chat_model() -> ChatGoogleGenerativeAI:
    global _chat_model
    if _chat_model is None:
        _chat_model = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.1,
            max_retries=settings.gemini_max_retries,
        )
    return _chat_model


def _get_structured_llm():
    global _structured_llm
    if _structured_llm is None:
        model = _get_chat_model()
        _structured_llm = model.with_structured_output(GroundedAnswer)
    return _structured_llm


def build_context(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Document: {chunk.document}]\n{chunk.text}")
    return "\n\n---\n\n".join(parts)


def answer_question(question: str, chunks: list[RetrievedChunk]) -> QueryResponse:
    if not chunks:
        return QueryResponse(
            answer=REFUSAL_MESSAGE,
            evidence=[],
        )

    context = build_context(chunks)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ])

    try:
        structured_llm = _get_structured_llm()
        chain = prompt | structured_llm
        result: GroundedAnswer = chain.invoke({"context": context, "question": question})

        return QueryResponse(
            answer=result.answer,
            evidence=result.evidence,
        )
    except Exception as e:
        logger.error(f"Structured response generation failed, falling back: {e}")
        try:
            model = _get_chat_model()
            chain = prompt | model
            res = chain.invoke({"context": context, "question": question})
            text = res.content if isinstance(res.content, str) else str(res.content)
            fallback_evidence = [
                EvidenceItem(source_document=c.document, excerpt=c.text[:200])
                for c in chunks[:1]
            ]
            return QueryResponse(
                answer=text.strip(),
                evidence=fallback_evidence,
            )
        except Exception as fallback_err:
            logger.error(f"Fallback generation failed: {fallback_err}")
            return QueryResponse(
                answer="An error occurred while generating the answer. Please try again.",
                evidence=[],
            )
