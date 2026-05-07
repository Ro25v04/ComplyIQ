from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from backend.config import settings
from backend.agent.tools.static_retriever import static_retriever
from backend.agent.tools.query_reformulator import query_reformulator
from backend.agent.tools.live_fetcher import live_fetcher
from backend.agent.tools.citation_validator import citation_validator
from backend.monitoring.langfuse_client import observe, get_client

MODEL = "gpt-4o-mini"

TOOLS = [
    query_reformulator,
    static_retriever,
    live_fetcher,
    citation_validator,
]

TOOL_REGISTRY = {
    "query_reformulator": query_reformulator,
    "static_retriever": static_retriever,
    "live_fetcher": live_fetcher,
    "citation_validator": citation_validator,
}

SYSTEM_PROMPT = """You are ComplyAU, an expert Australian compliance analyst.

You have access to the user's uploaded documents via static_retriever. NEVER ask the user to paste document text.

FACTUAL questions (who, what, when, where about the document):
- Call static_retriever ONCE, then answer immediately.
- Examples: "who are the parties?", "what is the term?", "what does clause X say?"

COMPLIANCE questions (is this compliant, what are the gaps, does this meet legal requirements):
- Call static_retriever ONCE, then live_fetcher ONCE (only if a specific Australian Act applies), then write your answer directly using this format:
  ### Gaps Found
  - [Gap]: description
  ### Compliant Areas
  - [Area]: description
  ### Recommendations
  - [Action]: description

FOLLOW-UP questions (referring to previous answers):
- Answer from conversation history directly. Do NOT call any tools.
- Examples: "so it is not a contract?", "what does that mean?"

NEVER call live_fetcher unless a specific Australian Act is clearly relevant.
NEVER call any tool more than once per question.
NEVER call gap_identifier — do the gap analysis yourself in your final answer.
Write your final answer immediately after getting tool results."""

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


def stream_agent(query: str, history: list[dict] | None = None):
    llm_with_tools = get_llm()
    streaming_llm = ChatOpenAI(
        model=MODEL,
        api_key=settings.openai_api_key,
        temperature=0.1,
    )

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in (history or []):
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=query))

    # Phase 1: Run tool calls (non-streaming)
    for _ in range(10):
        response = llm_with_tools.invoke(messages)

        if not response.tool_calls:
            break

        messages.append(response)
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"\n[Tool Call] {tool_name}({tool_args})")
            tool_fn = TOOL_REGISTRY.get(tool_name)
            tool_result = tool_fn.invoke(tool_args) if tool_fn else f"Unknown tool: {tool_name}"
            print(f"[Tool Result] {str(tool_result)[:200]}...")
            messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))

    # Phase 2: Stream the final answer
    for chunk in streaming_llm.stream(messages):
        if chunk.content:
            yield chunk.content
