from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
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

Process:
1. Call static_retriever to search the uploaded documents for relevant content
2. Call live_fetcher to find what Australian law requires on the topic
3. Call gap_identifier with the combined policy text and legal requirements to identify gaps
4. After receiving gap_identifier results, write your final answer directly — do NOT call any more tools

Keep tool calls to a minimum. Once you have results from static_retriever, live_fetcher, and gap_identifier, stop calling tools and write your final answer immediately.

Always cite sources. Never ask the user to paste document content."""

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
def run_agent(query: str) -> str:
    lf = get_client()
    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]

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
