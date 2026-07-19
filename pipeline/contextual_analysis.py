import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = spacy.load("en_core_web_sm")

def scan_contextual_analysis(text: str) -> dict:
    """
    Performs NLP Named Entity Recognition and structural intent scanning 
    to identify risky contextual categories.
    """
    doc = nlp(text)
    detected_risks = []
    risk_triggered = False
    
    # Context validation rules targeting specific high-risk entities
    # If the text explicitly targets entities like money, locations, or dates in combination with dark actions
    for ent in doc.ents:
        if ent.label_ in ["MONEY", "ORG"] and any(word in text.lower() for word in ["bypass", "leak", "hack", "transfer"]):
            risk_triggered = True
            detected_risks.append({
                "type": "Risky Entity Association",
                "matched_entity": ent.text,
                "label": ent.label_,
                "message": f"Suspicious entity action context surrounding: {ent.text} ({ent.label_})."
            })
            
    return {
        "risk_detected": risk_triggered,
        "findings": detected_risks,
        "module_risk_contribution": "Medium" if risk_triggered else "None"
    }