from langchain_core.tools import Tool
from backend.mcp_servers.legislation_au import fetch_legislation
from backend.mcp_servers.oaic import fetch_oaic

LEGISLATION_KEYWORDS = ["privacy act", "fair work act",
                        "corporations act", "work health and safety act"]
OAIC_KEYWORDS = ["data breach", "australian privacy principles",
                 "privacy impact", "credit reporting", "oaic"]


def fetch_live(query: str) -> str:
    key = query.lower()

    results = []

    for keyword in LEGISLATION_KEYWORDS:
        if keyword in key:
            results.append(fetch_legislation(query))
            break

    for keyword in OAIC_KEYWORDS:
        if keyword in key:
            results.append(fetch_oaic(query))
            break

    if not results:
        return (
            "No matching live source found. "
            "Try mentioning a specific act (e.g. Privacy Act 1988) "
            "or topic (e.g. data breach, Australian Privacy Principles)."
        )

    return "\n\n---\n\n".join(results)


# Langchain tool for the agent to fetch sources
live_fetcher_tool = Tool(
    name="live_fetcher",
    func=fetch_live,
    description=(
        "Fetch live regulatory information from Australian government websites. "
        "Use this when you need to know what the actual law or regulation says, "
        "not what the uploaded documents say. "
        "Input should mention a specific act (e.g. Privacy Act 1988, Fair Work Act 2009) "
        "or a topic (e.g. data breach, Australian Privacy Principles, credit reporting)."
    ),
)
