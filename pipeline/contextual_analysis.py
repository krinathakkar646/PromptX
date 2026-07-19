"""Context-aware risk detection based on risky actions and sensitive targets."""

import re
import spacy

from pipeline.security_utils import build_result


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # The module remains usable for keyword-based context checks when the model is absent.
    nlp = spacy.blank("en")


RISKY_ACTIONS = {
    "bypass": 15,
    "extract": 15,
    "exfiltrate": 20,
    "leak": 20,
    "steal": 20,
    "hack": 20,
    "transfer": 15,
    "send": 10,
    "disclose": 15,
}
SENSITIVE_TARGETS = r"\b(?:credentials?|passwords?|api\s*keys?|tokens?|customer\s+data|personal\s+data|pii|money|funds?|bank\s+account|confidential\s+(?:data|file|information))\b"


def scan_contextual_analysis(text: str) -> dict:
    """Flag risky intent only when an action is associated with a sensitive target."""
    normalized_text = " ".join(text.lower().split())
    doc = nlp(text)
    target_matches = [match.group(0) for match in re.finditer(SENSITIVE_TARGETS, normalized_text, re.IGNORECASE)]
    named_entities = [entity.text for entity in doc.ents if entity.label_ in {"MONEY", "ORG", "PERSON", "GPE"}]
    targets = list(dict.fromkeys(target_matches + named_entities))
    findings = []

    if not targets:
        return build_result(findings, maximum_score=20)

    for action, score in RISKY_ACTIONS.items():
        if re.search(rf"\b{re.escape(action)}\b", normalized_text):
            findings.append({
                "type": "Risky Intent Association",
                "matched_action": action,
                "matched_targets": targets[:3],
                "message": f"Risky action '{action}' is associated with sensitive target(s): {', '.join(targets[:3])}.",
                "score": score,
                "severity": "High" if score >= 15 else "Medium",
            })

    return build_result(findings, maximum_score=20)
