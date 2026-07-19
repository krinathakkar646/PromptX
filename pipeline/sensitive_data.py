"""Detection and safe redaction of sensitive credentials and contact data."""

import re

from pipeline.security_utils import build_result, mask_value


DETECTION_PATTERNS = [
    ("AWS Access Key", re.compile(r"\b(?:AKIA|ASCA|ASIA)[A-Z0-9]{16}\b"), 30),
    ("GitHub Token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"), 30),
    ("GitLab Token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"), 30),
    ("JWT Token", re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"), 25),
    ("Email Address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), 10),
    ("Phone Number", re.compile(r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"), 10),
    ("Password Assignment", re.compile(r"\b(?:password|passwd|pwd)\s*[:=]\s*['\"]?([^\s,'\";]{6,})", re.IGNORECASE), 25),
    ("API Secret Assignment", re.compile(r"\b(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|secret)\s*[:=]\s*['\"]?([A-Za-z0-9_-]{16,})", re.IGNORECASE), 25),
]

# Includes identifiers handled by the privacy module, so logs do not retain them.
REDACTION_PATTERNS = [
    pattern for _, pattern, _ in DETECTION_PATTERNS
] + [
    re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"),
    re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.IGNORECASE),
    re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"),
]


def _matched_value(match: re.Match) -> str:
    return match.group(1) if match.lastindex else match.group(0)


def redact_sensitive_data(text: str) -> str:
    """Mask credentials and PII before a prompt is written to persistent logs."""
    redacted = text
    for pattern in REDACTION_PATTERNS:
        redacted = pattern.sub(lambda match: mask_value(_matched_value(match)), redacted)
    return redacted


def scan_sensitive_data(text: str) -> dict:
    """Detect credentials and contact data without returning exposed values."""
    findings = []
    for label, pattern, score in DETECTION_PATTERNS:
        for match in pattern.finditer(text):
            value = _matched_value(match)
            findings.append({
                "type": label,
                "matched_value": mask_value(value),
                "message": f"Potential exposure of {label} detected.",
                "score": score,
                "severity": "Critical" if score >= 30 else "High" if score >= 20 else "Medium",
            })
    return build_result(findings, maximum_score=40)
