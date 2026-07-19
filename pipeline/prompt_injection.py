def scan_prompt_injection(text: str) -> dict:
    """
    Scans the input text for prompt injection keywords and malicious instruction overrides.
    """
    normalized_text = text.lower()
    
    # Common attack phrases used to hijack LLM behavior
    injection_indicators = [
        "ignore previous instructions",
        "ignore above instructions",
        "reveal system prompt",
        "reveal your system prompt",
        "act as administrator",
        "output hidden prompt",
        "override instruction",
        "you are now a bypass"
    ]
    
    detected_phrases = []
    risk_triggered = False

    for indicator in injection_indicators:
        if indicator in normalized_text:
            risk_triggered = True
            detected_phrases.append({
                "type": "Instruction Override",
                "matched_phrase": indicator,
                "message": f"Malicious prompt manipulation attempt detected: '{indicator}'"
            })

    return {
        "risk_detected": risk_triggered,
        "findings": detected_phrases,
        "module_risk_contribution": "High" if risk_triggered else "None"
    }