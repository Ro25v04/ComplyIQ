import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.security.presidio import anonymise

TEST_TEXTS = [
    # Names, email, phone
    "John Smith at john@acme.com called 0412 345 678 about a data breach",
    # TFN
    "Jane Doe's TFN is 123 456 789 and she lives at 123 George Street Sydney",
    # Medicare
    "Patient medicare number is 2123 45670 1",
    # Passport
    "Passport number N1234567 was verified",
    # BSB and bank account
    "BSB 012-345 account number 12345678",
    # ABN
    "The company ABN is 51 824 753 556",
    # Salary
    "Employee salary is $95,000.00 per annum as per the remuneration package",
    # Date of birth
    "Employee date of birth is 15/03/1990 as per employment records",
    # Regulatory text — should stay unchanged
    "The Privacy Act 1988 requires organisations to notify the OAIC within 30 days of an eligible data breach under the NDB scheme",
    # Mixed PII and regulatory
    "CEO Michael Johnson at michael@company.com.au must ensure compliance with the Fair Work Act 2009",
]


def test_presidio():
    for text in TEST_TEXTS:
        print(f"Original:   {text}")
        print(f"Anonymised: {anonymise(text)}")
        print("-" * 70)


if __name__ == "__main__":
    test_presidio()
