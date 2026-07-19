import re

def scan_privacy_compliance(text: str) -> dict:
    """
    Scans for personal data exposure, compliance flags, and organizational policy violations.
    """
    normalized_text = text.lower()
    
    # Matching common patterns for financial/personal data leaks
    compliance_patterns = {
        "Credit Card Pattern": r"\b(?:\d[ -]*?){13,16}\b",
        "Social Security / National ID": r"\b\d{3}-\d{2}-\d{4}\b|\b\d{4}[- ]?\d{4}[- ]?\d{4}\b"
    }
    
    # Keyword indicators for internal corporate confidentiality
    policy_keywords = [
        "confidential proprietary", 
        "internal use only", 
        "gdpr sensitive", 
        "restructured financial sheet"
    ]
    
    detected_violations = []
    risk_triggered = False

    # 1. Pattern matching
    for label, pattern in compliance_patterns.items():
        if re.search(pattern, text):
            risk_triggered = True
            detected_violations.append({
                "type": "Compliance Violation",
                "matched_indicator": label,
                "message": f"Sensitive structured personal identifier leaked ({label})."
            })
            
    # 2. Keyphrase policy check
    for keyword in policy_keywords:
        if keyword in normalized_text:
            risk_triggered = True
            detected_violations.append({
                "type": "Company Policy Breach",
                "matched_indicator": keyword,
                "message": f"Unauthorized transmission of corporate assets containing: '{keyword}'."
            })

    return {
        "risk_detected": risk_triggered,
        "findings": detected_violations,
        "module_risk_contribution": "Medium" if risk_triggered else "None"
    }