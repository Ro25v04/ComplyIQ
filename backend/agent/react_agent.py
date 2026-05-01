from groq import Groq
from backend.config import settings
from backend.agent.tools.static_retriever import static_retriever
from backend.agent.tools.query_reformulator import query_reformulator
from backend.agent.tools.live_fetcher import live_fetcher
from backend.agent.tools.gap_identifier import gap_identifier

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are ComplyAU, an expert Australian compliance analyst.
You will be given a compliance question along with:
- Company policy excerpts (from uploaded documents)
- Relevant Australian law (from legislation.gov.au and oaic.gov.au)
- A compliance gap analysis

Using all of this context, provide a clear, cited compliance assessment.
Always reference specific sources. Never guess. State insufficient evidence when needed."""


def run_agent(query: str) -> str:
    print(f"\n[Step 1] Reformulating query...")
    refined_query = query_reformulator.invoke({"query": query})
    print(f"Refined: {refined_query}")

    print(f"\n[Step 2] Searching uploaded documents...")
    policy_context = static_retriever.invoke({"query": refined_query})
    print(f"Found: {policy_context[:200]}...")

    print(f"\n[Step 3] Fetching live Australian law...")
    live_context = live_fetcher.invoke({"query": refined_query})
    print(f"Found: {live_context[:200]}...")

    print(f"\n[Step 4] Identifying compliance gaps...")
    gap_input = f"COMPANY POLICY:\n{policy_context}\n\nAUSTRALIAN LAW:\n{live_context}"
    gaps = gap_identifier.invoke({"input_text": gap_input})
    print(f"Gaps: {gaps[:200]}...")

    print(f"\n[Step 5] Generating final answer...")
    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": (
                f"QUESTION: {query}\n\n"
                f"COMPANY POLICY EXCERPTS:\n{policy_context}\n\n"
                f"AUSTRALIAN LAW:\n{live_context}\n\n"
                f"GAP ANALYSIS:\n{gaps}"
            )},
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content