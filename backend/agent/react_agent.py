from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_groq import ChatGroq
from backend.config import settings
from backend.agent.tools.static_retriever import static_retriever_tool
from backend.agent.tools.query_reformulator import query_reformulator_tool
from backend.agent.tools.live_fetcher import live_fetcher_tool
from backend.agent.tools.citation_validator import citation_validator_tool
from backend.agent.tools.gap_identifier import gap_identifier_tool

MODEL = "llama-3.3-70b-versatile"

# Tools available to the agent
TOOLS = [
    query_reformulator_tool,
    static_retriever_tool,
    live_fetcher_tool,
    citation_validator_tool,
    gap_identifier_tool,
]

_agent_executor = None


def get_agent_executor() -> AgentExecutor:
    global _agent_executor
    if _agent_executor is None:
        llm = ChatGroq(
            model=MODEL,
            api_key=settings.groq_api_key,
            temperature=0.1,
        )

        prompt = hub.pull("hwchase17/react")

        agent = create_react_agent(llm=llm, tools=TOOLS, prompt=prompt)

        _agent_executor = AgentExecutor(
            agent=agent,
            tools=TOOLS,
            verbose=True,
            max_iterations=8,
            handle_parsing_errors=True,
        )

    return _agent_executor


def run_agent(query: str) -> str:
    executor = get_agent_executor()
    result = executor.invoke({"input": query})
    return result["output"]