# PII anonymisation

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# PII types to detect and mask
PII_ENTITIES = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "LOCATION",
    "DATE_TIME",
    "CREDIT_CARD",
    "AU_TFN",        # Australian Tax File Number
    "AU_ABN",        # Australian Business Number
    "AU_ACN",        # Australian Company Number
]

# Load engines once at module level
_analyzer = None
_anonymizer = None


def get_engines():
    global _analyzer, _anonymizer
    if _analyzer is None:
        _analyzer = AnalyzerEngine()
        _anonymizer = AnonymizerEngine()
    return _analyzer, _anonymizer


def anonymise(text: str) -> str:
    if not text or not text.strip():
        return text

    analyzer, anonymizer = get_engines()

    # detect PII entities in the text
    results = analyzer.analyze(
        text=text,
        entities=PII_ENTITIES,
        language="en"
    )

    # replace detected PII with placeholders
    anonymised = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )

    return anonymised.text
