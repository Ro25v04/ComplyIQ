import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain_core.tools import tool
from mcp import ClientSession
from mcp.client.sse import sse_client
from backend.config import settings

LEGISLATION_KEYWORDS = [
    "privacy act", "fair work act", "corporations act",
    "work health and safety act", "competition and consumer act",
    "australian consumer law", "superannuation guarantee",
    "spam act", "age discrimination act", "national employment standards",
    "unpaid internship",
]
OAIC_KEYWORDS = [
    "data breach", "australian privacy principles",
    "privacy impact", "credit reporting", "oaic",
]


async def _call_mcp_tool(tool_name: str, args: dict) -> str:
    async with sse_client(settings.mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, args)
            return result.content[0].text if result.content else "No result returned."


def _run_async(tool_name: str, args: dict) -> str:
    # FastAPI runs inside an existing event loop, so asyncio.run() raises
    # "This event loop is already running". Spawning a fresh loop in a thread
    # sidesteps the conflict while keeping the call synchronous to LangChain tools.
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_call_mcp_tool(tool_name, args))
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(run_in_thread)
        return future.result()


@tool
def live_fetcher(query: str) -> str:
    """Fetch live regulatory information from Australian government websites.
    Use this when you need to know what the actual law or regulation says,
    not what the uploaded documents say.
    Input should mention a specific act (e.g. Privacy Act 1988, Fair Work Act 2009)
    or a topic (e.g. data breach, Australian Privacy Principles, credit reporting)."""
    key = query.lower()
    results = []

    for keyword in LEGISLATION_KEYWORDS:
        if keyword in key:
            results.append(_run_async("fetch_legislation_tool", {"act_name": query}))
            break

    for keyword in OAIC_KEYWORDS:
        if keyword in key:
            results.append(_run_async("fetch_oaic_guidance", {"topic": query}))
            break

    if not results:
        return (
            "No matching live source found. "
            "Try mentioning a specific act (e.g. Privacy Act 1988) "
            "or topic (e.g. data breach, Australian Privacy Principles)."
        )

    return "\n\n---\n\n".join(results)