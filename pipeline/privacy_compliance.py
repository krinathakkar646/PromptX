"""Privacy and compliance checks for structured identifiers and data labels."""

import re

from pipeline.security_utils import build_result, mask_value


def _passes_luhn(number: str) -> bool:
    digits = [int(character) for character in number if character.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


POLICY_LABELS = [
    ("Confidential Data Label", r"\b(?:confidential|restricted|internal\s+use\s+only|private)\b", 10),
    ("Privacy Regulation Reference", r"\b(?:gdpr\s+sensitive|personal\s+data|personally\s+identifiable\s+information|pii)\b", 15),
    ("Unauthorised Sharing Request", r"\b(?:do\s+not\s+share|keep\s+(?:this\s+)?secret|send\s+this\s+externally)\b", 15),
]


def scan_privacy_compliance(text: str) -> dict:
    """Detect PII, valid payment-card numbers, and confidential-data labels."""
    findings = []

    for match in re.finditer(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)", text):
        candidate = match.group(0)
        if _passes_luhn(candidate):
            findings.append({
                "type": "Payment Card Number",
                "matched_indicator": mask_value(candidate),
                "message": "A payment-card-like number that passes checksum validation was detected.",
                "score": 30,
                "severity": "Critical",
            })

    identifiers = [
        ("PAN Number", r"\b[A-Z]{5}\d{4}[A-Z]\b", 25),
        ("Aadhaar-like Identifier", r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b", 25),
        ("US Social Security Number", r"\b\d{3}-\d{2}-\d{4}\b", 25),
    ]
    for label, pattern, score in identifiers:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            findings.append({
                "type": label,
                "matched_indicator": mask_value(match.group(0)),
                "message": f"Potential {label.lower()} exposure detected.",
                "score": score,
                "severity": "High",
            })

    for label, pattern, score in POLICY_LABELS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            findings.append({
                "type": label,
                "matched_indicator": match.group(0),
                "message": f"Potential privacy or policy concern: {match.group(0)}.",
                "score": score,
                "severity": "Medium",
            })

    return build_result(findings, maximum_score=35)
