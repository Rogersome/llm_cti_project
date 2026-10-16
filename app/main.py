import logging
from contextlib import asynccontextmanager

from anthropic import APIError, APITimeoutError
from fastapi import FastAPI, HTTPException

from app.config import settings
from app.schemas import AskRequest, AskResponse, HealthResponse
from app.service import RagService

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

state: dict[str, RagService] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時建立一次索引，之後每個請求重複使用
    state["service"] = RagService()
    yield
    state.clear()


app = FastAPI(
    title="Cybersecurity RAG API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    service = state.get("service")
    if service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    return HealthResponse(status="ok", documents_loaded=service.document_count)


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    service = state.get("service")
    if service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    try:
        return service.ask(request.question)
    except APITimeoutError:
        logger.exception("Upstream timeout")
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except APIError:
        logger.exception("Upstream API error")
        raise HTTPException(status_code=502, detail="LLM service unavailable")