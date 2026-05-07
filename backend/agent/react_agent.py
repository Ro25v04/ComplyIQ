from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from backend.config import settings
from backend.agent.tools.static_retriever import static_retriever
from backend.agent.tools.query_reformulator import query_reformulator
from backend.agent.tools.live_fetcher import live_fetcher
from backend.agent.tools.citation_validator import citation_validator
from backend.agent.tools.gap_identifier import gap_identifier
from backend.monitoring.langfuse_client import observe, get_client

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

IMPORTANT: You have access to the user's uploaded documents via the static_retriever tool. NEVER ask the user to provide document text — always call static_retriever first to search for it.

Follow these rules strictly:

FACTUAL questions (who, what, when, where about the document):
- Call static_retriever ONLY, then answer immediately. No other tools needed.
- Examples: "who are the parties?", "what is the term?", "what does clause X say?", "is there a confidentiality clause?"

COMPLIANCE questions (is this compliant, what are the gaps, does this meet legal requirements):
- Call static_retriever, then live_fetcher (only if a named Australian Act applies), then gap_identifier, then answer.
- Examples: "does this comply with the Fair Work Act?", "what are the compliance gaps?", "is this agreement lawful?"

FOLLOW-UP questions (referring to previous answers):
- Answer from conversation history directly. Do NOT call any tools unless new information is needed.
- Examples: "so it is not a contract?", "what does that mean?", "can you elaborate?"

NEVER call live_fetcher unless a specific Australian Act (Privacy Act, Fair Work Act, etc.) is clearly relevant.
NEVER call static_retriever more than once per question — if the first result doesn't contain the answer, say so and answer from what you have.
NEVER call more than one tool when a factual answer is enough.
Write your final answer immediately after you have enough information."""

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


@observe()
def run_agent(query: str, history: list[dict] | None = None) -> str:
    lf = get_client()
    llm = get_llm()

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for msg in (history or []):
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=query))

    final_answer = "Agent reached maximum iterations without a final answer."

    for _ in range(15):
        response = llm.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            final_answer = response.content or "No response generated."
            break

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"\n[Tool Call] {tool_name}({tool_args})")

            with lf.start_as_current_observation(name=tool_name, input=tool_args):
                tool_fn = TOOL_REGISTRY.get(tool_name)
                tool_result = tool_fn.invoke(tool_args) if tool_fn else f"Unknown tool: {tool_name}"
                lf.update_current_span(output=str(tool_result)[:500])

            print(f"[Tool Result] {str(tool_result)[:200]}...")

            messages.append(ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"],
            ))

    return final_answer
