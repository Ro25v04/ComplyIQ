from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agent.react_agent import run_agent

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer = run_agent(request.question)
    return QueryResponse(answer=answer)
