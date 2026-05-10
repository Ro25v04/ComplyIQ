from fastapi import APIRouter
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config import settings
import json

router = APIRouter()

MODEL = "gpt-4o-mini"

REPORT_PROMPT = """You are a compliance analysis AI. Given a conversation between a user and a compliance assistant about an Australian legal document, extract all compliance gaps and issues mentioned.

Return a JSON object with this exact structure:
{
  "document_name": "name of the document being analyzed (or 'Compliance Document' if not mentioned)",
  "gaps": [
    {
      "regulation": "Name of the Australian Act or Regulation",
      "description": "Brief description of the specific gap or issue",
      "severity": "critical"
    }
  ],
  "recommendations": [
    {
      "title": "Short action title (5 words max)",
      "description": "What specifically needs to be done to fix this"
    }
  ]
}

Severity rules:
- critical: Missing required legal clauses, illegal terms, major non-compliance that could result in penalties
- major: Important gaps that need prompt attention but are not immediately illegal
- minor: Best practice improvements, minor gaps, suggested enhancements

Extract up to 6 gaps and 3 recommendations from the conversation.
Return ONLY valid JSON — no markdown, no code fences, no explanation."""


class ReportRequest(BaseModel):
    history: list[dict]


@router.post("/report/generate")
def generate_report(request: ReportRequest):
    llm = ChatOpenAI(model=MODEL, api_key=settings.openai_api_key, temperature=0)

    conversation_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in request.history
    ])

    messages = [
        SystemMessage(content=REPORT_PROMPT),
        HumanMessage(content=f"Here is the conversation to analyze:\n\n{conversation_text}"),
    ]

    response = llm.invoke(messages)

    try:
        data = json.loads(response.content)
    except json.JSONDecodeError:
        content = response.content
        start = content.find("{")
        end = content.rfind("}") + 1
        data = json.loads(content[start:end])

    gaps = data.get("gaps", [])

    score = 100
    for gap in gaps:
        severity = gap.get("severity", "minor")
        if severity == "critical":
            score -= 20
        elif severity == "major":
            score -= 10
        else:
            score -= 5
    score = max(0, score)

    if score >= 80:
        risk_level = "Low"
    elif score >= 60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "document_name": data.get("document_name", "Compliance Document"),
        "score": score,
        "risk_level": risk_level,
        "gaps": gaps,
        "recommendations": data.get("recommendations", []),
    }