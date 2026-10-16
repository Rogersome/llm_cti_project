from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)


class Source(BaseModel):
    rank: int
    score: float
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    model: str
    latency_ms: int


class HealthResponse(BaseModel):
    status: str
    documents_loaded: int