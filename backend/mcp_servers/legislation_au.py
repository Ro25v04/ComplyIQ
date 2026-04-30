import requests    # http requests to websites
from bs4 import BeautifulSoup

BASE_URL = "https://www.legislation.gov.au"

KNOWN_ACTS = {
    "privacy act 1988": "/Details/C2022C00285",
    "fair work act 2009": "/Details/C2023C00059",
    "corporations act 2001": "/Details/C2023C00001",
    "work health and safety act 2011": "/Details/C2022C00196",
}

HEADERS = {"User-Agent": "ComplyAU/1.0 (compliance research tool)"}

# inputs the name of the act and outputs the content


def fetch_legislation(act_name: str) -> str:
    key = act_name.lower().strip()

    path = None
    for known_name, known_path in KNOWN_ACTS.items():
        if known_name in key or key in known_name:
            path = known_path
            break

    if not path:
        return f"Could not find legislation for: {act_name}. Known acts: {', '.join(KNOWN_ACTS.keys())}"

    url = BASE_URL + path
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Failed to fetch legislation from {url}: {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    main = soup.find("main") or soup.find("div", class_="content") or soup.body
    text = main.get_text(separator="\n", strip=True) if main else soup.get_text(
        separator="\n", strip=True)

    lines = [line for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines[:200])

    return f"[legislation.gov.au — {act_name}]\n\n{cleaned}"
