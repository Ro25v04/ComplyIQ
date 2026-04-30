import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.oaic.gov.au"

KNOWN_TOPICS = {
    "data breach": "/privacy/notifiable-data-breaches",
    "australian privacy principles": "/privacy/australian-privacy-principles",
    "privacy impact assessment": "/privacy/privacy-impact-assessments",
    "credit reporting": "/privacy/credit-reporting",
}

HEADERS = {"User-Agent": "ComplyAU/1.0 (compliance research tool)"}


def fetch_oaic(topic: str) -> str:
    key = topic.lower().strip()

    path = None
    for known_name, known_path in KNOWN_TOPICS.items():
        if known_name in key or key in known_name:
            path = known_path
            break

    if not path:
        return f"Could not find OAIC guidance for: {topic}. Known topics: {', '.join(KNOWN_TOPICS.keys())}"

    url = BASE_URL + path
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Failed to fetch OAIC guidance from {url}: {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    main = soup.find("main") or soup.find("div", class_="content") or soup.body
    text = main.get_text(separator="\n", strip=True) if main else soup.get_text(separator="\n", strip=True)

    lines = [line for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines[:200])

    return f"[oaic.gov.au — {topic}]\n\n{cleaned}"