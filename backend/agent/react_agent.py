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
- Call static_retriever ONCE to retrieve the document content
- Call live_fetcher for EACH relevant Australian Act that applies to the document type. For an internship/employment document check: Fair Work Act 2009, Work Health and Safety Act 2011, and any other relevant acts. For a privacy/data document check: Privacy Act 1988, Spam Act 2003. For a business document check: Corporations Act 2001, Australian Consumer Law.
- After getting all results, write your answer covering each Act checked using this format:
  ### [Act Name]
  #### Gaps Found
  - [Gap]: description
  #### Compliant Areas
  - [Area]: description
  #### Recommendations
  - [Action]: description

FOLLOW-UP questions (referring to previous answers):
- Answer from conversation history directly. Do NOT call any tools.
- Examples: "so it is not a contract?", "what does that mean?"

NEVER call static_retriever more than once per question.
You MAY call live_fetcher multiple times — once per relevant Act — but only for Acts that genuinely apply to the document type.
NEVER call gap_identifier — do the gap analysis yourself in your final answer.
You are an expert on Australian law and MUST answer any question about Australian legislation, acts, regulations, or compliance topics freely from your own knowledge.
Only refuse questions that are completely unrelated to law or business (e.g. "who is LeBron James", "how do I cook pasta"). For those say: "I can only assist with compliance documents and Australian law."
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
    lf = get_client()
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

    with lf.start_as_current_observation(name="stream_agent", input={"query": query}):
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
                with lf.start_as_current_observation(name=tool_name, input=tool_args):
                    tool_fn = TOOL_REGISTRY.get(tool_name)
                    tool_result = tool_fn.invoke(tool_args) if tool_fn else f"Unknown tool: {tool_name}"
                    lf.update_current_span(output=str(tool_result)[:500])
                print(f"[Tool Result] {str(tool_result)[:200]}...")
                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))

        # Phase 2: Stream the final answer, collect full text for logging
        full_response = ""
        for chunk in streaming_llm.stream(messages):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content

        lf.update_current_span(output={"response": full_response[:1000]})
