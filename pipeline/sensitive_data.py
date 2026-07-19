import re

def scan_sensitive_data(text: str) -> dict:
    """
    Scans the input text for PII, secrets, and credentials using Regex patterns.
    """
    # Define robust regex signatures for critical sensitive data types
    patterns = {
        "AWS Access Key": r"\b(AKIA|ASCA|ASIA)[A-Z0-9]{16}\b",
        "Email Address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "Phone Number": r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b",
        "Generic API Token": r"\b[a-zA-Z0-9-_]{32,64}\b"
    }
    
    detected_issues = []
    risk_triggered = False

    for label, regex_pattern in patterns.items():
        matches = re.findall(regex_pattern, text)
        if matches:
            risk_triggered = True
            for match in matches:
                # If a match is a tuple (due to capturing groups), flatten it to a string
                match_str = match if isinstance(match, str) else match[0]
                detected_issues.append({
                    "type": label,
                    "matched_value": match_str,
                    "message": f"Potential leak of {label} detected."
                })

    return {
        "risk_detected": risk_triggered,
        "findings": detected_issues,
        "module_risk_contribution": "High" if risk_triggered else "None"
    }