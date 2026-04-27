# PII anonymisation using Microsoft Presidio — runs locally, no external API

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

PII_ENTITIES = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "LOCATION",
    "CREDIT_CARD",
    "IP_ADDRESS",
    "AU_TFN",
    "AU_ABN",
    "AU_ACN",
    "AU_MEDICARE",
    "AU_PASSPORT",
    "AU_DRIVERS_LICENCE",
    "AU_BSB",
    "AU_BANK_ACCOUNT",
]

# Terms that should never be anonymised
WHITELIST = [
    # Australian legislation
    "Privacy Act 1988",
    "Fair Work Act 2009",
    "Corporations Act 2001",
    "Migration Act 1958",
    "Work Health and Safety Act 2011",
    "Privacy Act",
    "Fair Work Act",
    "Corporations Act",
    # Government bodies
    "OAIC", "ASIC", "ATO", "APRA", "ACCC", "AHRC",
    "Fair Work Commission", "Fair Work Ombudsman",
    # Regulatory terms
    "NDB", "APP", "GDPR", "ISO", "SOC2",
    # Job titles
    "CEO", "CFO", "CTO", "COO", "HR",
    # Common legal years that are NOT dates of birth
    "1988", "2009", "2001", "1958", "2011",
]

_analyzer = None
_anonymizer = None


def _build_analyzer() -> AnalyzerEngine:
    analyzer = AnalyzerEngine()

    # Australian Tax File Number — 8 or 9 digits
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AU_TFN",
        patterns=[Pattern("au_tfn", r"\b\d{3}\s?\d{3}\s?\d{3}\b", 0.7)],
        context=["tfn", "tax file", "tax file number"],
    ))

    # Australian Business Number — 11 digits
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AU_ABN",
        patterns=[Pattern("au_abn", r"\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b", 0.7)],
        context=["abn", "australian business number"],
    ))

    # Australian Company Number — 9 digits
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AU_ACN",
        patterns=[Pattern("au_acn", r"\b\d{3}\s?\d{3}\s?\d{3}\b", 0.7)],
        context=["acn", "australian company number"],
    ))

    # Medicare number — 10 digits
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AU_MEDICARE",
        patterns=[Pattern("au_medicare", r"\b\d{4}\s?\d{5}\s?\d\b", 0.7)],
        context=["medicare", "medicare number", "medicare card"],
    ))

    # Australian passport — letter followed by 7 digits
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AU_PASSPORT",
        patterns=[Pattern("au_passport", r"\b[A-Za-z]\d{7}\b", 0.6)],
        context=["passport", "passport number"],
    ))

    # Australian driver's licence — varies by state, general pattern
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AU_DRIVERS_LICENCE",
        patterns=[Pattern("au_drivers_licence", r"\b\d{6,9}\b", 0.5)],
        context=["licence", "license", "driver", "drivers licence", "driving licence"],
    ))

    # BSB number — 6 digits with optional dash
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AU_BSB",
        patterns=[Pattern("au_bsb", r"\b\d{3}-?\d{3}\b", 0.6)],
        context=["bsb", "bank state branch"],
    ))

    # Bank account number — 6 to 10 digits
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AU_BANK_ACCOUNT",
        patterns=[Pattern("au_bank_account", r"\b\d{6,10}\b", 0.5)],
        context=["account", "account number", "bank account"],
    ))

    return analyzer


def get_engines():
    global _analyzer, _anonymizer
    if _analyzer is None:
        _analyzer = _build_analyzer()
        _anonymizer = AnonymizerEngine()
    return _analyzer, _anonymizer


def _remove_whitelisted(text: str, results: list) -> list:
    filtered = []
    for result in results:
        detected_text = text[result.start:result.end]
        if not any(term.lower() in detected_text.lower() for term in WHITELIST):
            filtered.append(result)
    return filtered


def anonymise(text: str) -> str:
    if not text or not text.strip():
        return text

    analyzer, anonymizer = get_engines()

    results = analyzer.analyze(
        text=text,
        entities=PII_ENTITIES,
        language="en"
    )

    results = _remove_whitelisted(text, results)

    if not results:
        return text

    anonymised = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )

    return anonymised.text
