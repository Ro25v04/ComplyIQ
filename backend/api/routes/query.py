from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.agent.react_agent import run_agent, stream_agent

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    history: list[dict] = []


class QueryResponse(BaseModel):
    answer: str


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer = run_agent(request.question, history=request.history)
    return QueryResponse(answer=answer)


@router.post("/query/stream")
def query_stream(request: QueryRequest):
    def generate():
        for chunk in stream_agent(request.question, history=request.history):
            yield chunk
    return StreamingResponse(generate(), media_type="text/plain")
