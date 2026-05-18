from openai import OpenAI
from backend.config import settings

_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def is_compliance_document(first_page_text: str) -> bool:
    # Only the first 1500 characters of the first page are sent — enough to
    # determine document type cheaply without processing the full content
    prompt = """You are a document classifier. Determine if the following document is a compliance, legal, or regulatory document.

This includes: contracts, agreements, policies, terms of service, privacy policies, employment agreements, NDAs, regulatory filings, codes of conduct, or any document that outlines legal obligations or rights.

This does NOT include: news articles, academic papers, spreadsheets, invoices, resumes, or general business documents unrelated to legal compliance.

Respond with only YES or NO.

Document text:
{text}""".format(text=first_page_text[:1500])

    response = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=5,
    )
    answer = response.choices[0].message.content.strip().upper()
    return answer == "YES"