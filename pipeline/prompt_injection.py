"""Prompt-injection detector with phrase and instruction-override patterns."""

import re

from pipeline.security_utils import build_result


INJECTION_PATTERNS = [
    ("Instruction Override", r"\bignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions?\b", 25),
    ("Instruction Override", r"\b(?:disregard|forget)\s+(?:all\s+)?(?:your|the|previous)\s+(?:rules|instructions)\b", 25),
    ("System Prompt Extraction", r"\b(?:reveal|show|output|print)\s+(?:your\s+)?(?:hidden\s+)?(?:system\s+prompt|system\s+message|instructions?)\b", 30),
    ("Role Manipulation", r"\b(?:act|behave|respond)\s+as\s+(?:an?\s+)?(?:administrator|developer|system)\b", 20),
    ("Policy Override", r"\b(?:override|bypass|disable)\s+(?:the\s+)?(?:safety|security|content)\s+(?:rules|policy|filters?)\b", 25),
    ("Data Exfiltration", r"\b(?:extract|leak|send|exfiltrate)\s+(?:the\s+)?(?:hidden|private|confidential|system)\s+(?:data|prompt|instructions?)\b", 25),
]


def scan_prompt_injection(text: str) -> dict:
    """Identify attempts to override instructions or expose protected context."""
    normalized_text = " ".join(text.lower().split())
    findings = []
    for category, pattern, score in INJECTION_PATTERNS:
        for match in re.finditer(pattern, normalized_text, re.IGNORECASE):
            phrase = match.group(0)
            findings.append({
                "type": category,
                "matched_phrase": phrase,
                "message": f"Potential {category.lower()} attempt detected.",
                "score": score,
                "severity": "Critical" if score >= 30 else "High",
            })
    return build_result(findings, maximum_score=35)
