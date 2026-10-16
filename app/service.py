import logging
import time

from anthropic import Anthropic, APIError, APITimeoutError

from app.config import settings
from app.schemas import AskResponse, Source
from src.rag import SimpleRAG

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are a cybersecurity assistant.

Answer ONLY using the context below. If the context does not contain the
answer, reply exactly: "No relevant information found in the knowledge base."

Context:
{context}

Question:
{question}

Answer with:
- Summary
- Threat mapping
- Defense"""

NO_MATCH = "No relevant information found in the knowledge base."


class RagService:
    def __init__(self) -> None:
        with open(settings.docs_path, encoding="utf-8") as f:
            docs = [d.strip() for d in f.read().split("\n---\n") if d.strip()]
        if not docs:
            raise RuntimeError(f"No documents loaded from {settings.docs_path}")
        self.rag = SimpleRAG(docs)
        self.client = Anthropic(
            api_key=settings.anthropic_api_key,
            timeout=30.0,
            max_retries=2,
        )
        logger.info("Loaded %d documents", len(docs))

    @property
    def document_count(self) -> int:
        return len(self.rag.docs)

    def ask(self, question: str) -> AskResponse:
        started = time.perf_counter()

        retrieved = self.rag.retrieve(question, top_k=settings.top_k)
        relevant = [
            (doc, score)
            for doc, score in retrieved
            if score >= settings.similarity_threshold
        ]

        if not relevant:
            logger.info(
                "No passage above threshold %.3f (best=%.3f)",
                settings.similarity_threshold,
                retrieved[0][1] if retrieved else 0.0,
            )
            return AskResponse(
                answer=NO_MATCH,
                sources=[],
                model=settings.model_name,
                latency_ms=int((time.perf_counter() - started) * 1000),
            )

        context = "\n\n".join(doc for doc, _ in relevant)
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)

        response = self.client.messages.create(
            model=settings.model_name,
            max_tokens=settings.max_tokens,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"temperature": 0},
        )
        answer = response.content[0].text

        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Answered in %dms | passages=%d | top_score=%.3f",
            latency_ms,
            len(relevant),
            relevant[0][1],
        )

        return AskResponse(
            answer=answer,
            sources=[
                Source(rank=i + 1, score=round(score, 4), excerpt=doc[:200])
                for i, (doc, score) in enumerate(relevant)
            ],
            model=settings.model_name,
            latency_ms=latency_ms,
        )