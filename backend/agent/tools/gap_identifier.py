from langchain_core.tools import tool
from backend.llm.generator import get_client

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert Australian compliance analyst.
You will be given two pieces of text:
1. What the company policy says
2. What the actual Australian law or regulation requires

Your job is to identify compliance gaps — where the company policy falls short of,
contradicts, or fails to address what the law requires.

Return your response in this format:
GAPS FOUND:
- [Gap 1]: brief description of the gap
- [Gap 2]: brief description of the gap

COMPLIANT AREAS:
- [Area 1]: what is already compliant

RECOMMENDATIONS:
- [Recommendation 1]: specific action to close the gap

If no gaps are found, state: "No compliance gaps identified."
"""


@tool
def gap_identifier(input_text: str) -> str:
    """Identify compliance gaps between a company policy and Australian law.
    Use this tool when you have retrieved both what the company policy says
    and what the actual legislation or regulation requires.
    Input should contain both the policy text and the legal requirement text
    so they can be compared.
    Returns a list of gaps, compliant areas, and recommendations."""
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input_text},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()