from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from backend.config import settings
from backend.agent.tools.static_retriever import static_retriever
from backend.agent.tools.query_reformulator import query_reformulator
from backend.agent.tools.live_fetcher import live_fetcher
from backend.agent.tools.citation_validator import citation_validator
from backend.agent.tools.gap_identifier import gap_identifier

MODEL = "gpt-4o-mini"

TOOLS = [
    query_reformulator,
    static_retriever,
    live_fetcher,
    citation_validator,
    gap_identifier,
]

TOOL_REGISTRY = {
    "query_reformulator": query_reformulator,
    "static_retriever": static_retriever,
    "live_fetcher": live_fetcher,
    "citation_validator": citation_validator,
    "gap_identifier": gap_identifier,
}

SYSTEM_PROMPT = """You are ComplyAU, an expert Australian compliance analyst.
Answer compliance questions by using your available tools.

Process:
1. Use query_reformulator for vague questions
2. Use static_retriever to find what company documents say
3. Use live_fetcher to find what Australian law requires
4. Use gap_identifier to compare the two and find gaps
5. Use citation_validator to verify citations

Always cite sources. Never guess. State insufficient evidence when needed."""

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=MODEL,
            api_key=settings.openai_api_key,
            temperature=0.1,
        ).bind_tools(TOOLS)
    return _llm


def run_agent(query: str) -> str:
    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]

    for _ in range(8):
        response = llm.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content or "No response generated."

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"\n[Tool Call] {tool_name}({tool_args})")

            tool_fn = TOOL_REGISTRY.get(tool_name)
            if tool_fn:
                tool_result = tool_fn.invoke(tool_args)
            else:
                tool_result = f"Unknown tool: {tool_name}"

            print(f"[Tool Result] {str(tool_result)[:200]}...")

            messages.append(ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"],
            ))

    return "Agent reached maximum iterations without a final answer."
