"""Detection of jailbreak personas and safety-bypass instructions."""

import re

from pipeline.security_utils import build_result


JAILBREAK_PATTERNS = [
    ("Known Jailbreak Persona", r"\b(?:dan\s+mode|do\s+anything\s+now)\b", 30),
    ("Safety Bypass", r"\b(?:ignore|remove|disable)\s+(?:all\s+)?(?:restrictions|safety\s+policies|ethical\s+limits)\b", 30),
    ("Unaligned Role-play", r"\b(?:pretend|act)\s+(?:that\s+)?you\s+(?:are\s+)?(?:unaligned|uncensored|without\s+(?:rules|restrictions))\b", 25),
    ("Developer-mode Claim", r"\b(?:developer\s+mode|god\s+mode|unrestricted\s+mode)\s+(?:enabled|on|activated)?\b", 25),
    ("Harmful Hypothetical Framing", r"\b(?:for\s+(?:an?\s+)?(?:fictional|hypothetical|educational)\s+(?:scenario|purpose))\b.*\b(?:bypass|hack|steal|exploit)\b", 20),
    ("Malicious Persuasion", r"\b(?:malicious\s+persuasion|jailbreak\s+prompt)\b", 20),
]


def scan_jailbreak(text: str) -> dict:
    """Identify jailbreak-style requests without relying only on exact keywords."""
    normalized_text = " ".join(text.lower().split())
    findings = []
    for category, pattern, score in JAILBREAK_PATTERNS:
        for match in re.finditer(pattern, normalized_text, re.IGNORECASE):
            findings.append({
                "type": category,
                "matched_signature": match.group(0),
                "message": f"Potential {category.lower()} detected.",
                "score": score,
                "severity": "Critical" if score >= 30 else "High",
            })
    return build_result(findings, maximum_score=45)
