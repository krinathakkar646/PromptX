from flask import Flask, request, jsonify
from pipeline.preprocessor import clean_and_tokenize
from pipeline.sensitive_data import scan_sensitive_data
from pipeline.prompt_injection import scan_prompt_injection
from pipeline.jailbreak import scan_jailbreak
from pipeline.privacy_compliance import scan_privacy_compliance
from pipeline.contextual_analysis import scan_contextual_analysis
from pipeline.logger import init_db, log_incident  # Import internal local storage

app = Flask(__name__)

# Initialize the SQLite database on startup
init_db()

@app.route('/')
def home():
    return "PromptX 5-Module Pipeline Gateway is fully operational!"

@app.route('/api/analyze', methods=['POST'])
def analyze_prompt():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400
    
    user_prompt = data['prompt']
    
    # 1. Run text cleaning preprocessing (Step 2)
    preprocessed_data = clean_and_tokenize(user_prompt)
    
    # 2. Parallel Core Security Screening (Step 3)
    m31_sensitive = scan_sensitive_data(user_prompt)
    m32_injection = scan_prompt_injection(user_prompt)
    m33_jailbreak = scan_jailbreak(user_prompt)
    m34_compliance = scan_privacy_compliance(user_prompt)
    m35_contextual = scan_contextual_analysis(user_prompt)
    
    # 3. Dynamic Local Scoring Engine (Calculated directly to save scope)
    base_score = 0
    triggered_modules = []
    
    if m31_sensitive["risk_detected"]:
        base_score += 40
        triggered_modules.append("Sensitive Data Leakage")
    if m32_injection["risk_detected"]:
        base_score += 35
        triggered_modules.append("Prompt Injection Attack")
    if m33_jailbreak["risk_detected"]:
        base_score += 45
        triggered_modules.append("Adversarial Jailbreak Attempt")
    if m34_compliance["risk_detected"]:
        base_score += 25
        triggered_modules.append("Compliance Policy Breach")
    if m35_contextual["risk_detected"]:
        base_score += 15
        triggered_modules.append("Risky Semantic Context")

    final_score = min(base_score, 100)
    
    # Local Risk Indexing Classification
    if final_score >= 75:
        risk_class = "Critical"
    elif final_score >= 50:
        risk_class = "High"
    elif final_score >= 25:
        risk_class = "Medium"
    elif final_score > 0:
        risk_class = "Low"
    else:
        risk_class = "Safe"
        
    final_status = "Flagged/Blocked" if final_score > 0 else "Safe"
    
    # Dynamic Explanations & Actionable Mitigations
    recommendations = []
    explanation = "No security issues or adversarial vectors were identified within the prompt input."
    
    if final_score > 0:
        explanation = f"Security pipeline flagged anomalies relating to: {', '.join(triggered_modules)}."
        recommendations.append("Do not submit this prompt to public AI systems in its current form.")
        if "Sensitive Data Leakage" in triggered_modules:
            recommendations.append("Action: Redact or replace all exposed API keys, passwords, or cloud credentials.")
        if "Prompt Injection Attack" in triggered_modules or "Adversarial Jailbreak Attempt" in triggered_modules:
            recommendations.append("Action: Remove system prompt manipulation keyphrases (e.g., 'ignore instructions').")
        if "Compliance Policy Breach" in triggered_modules:
            recommendations.append("Action: Clean the text of protected personal data (PII) or credit card strings.")

    # 4. Step 9: Log transaction securely into internal SQLite storage
    log_incident(
        raw_prompt=user_prompt,
        status=final_status,
        risk_score=final_score,
        risk_classification=risk_class
    )
    
    # Construct complete unified report payload
    response_payload = {
        "status": final_status,
        "risk_classification": risk_class,
        "risk_scoring_engine": {
            "calculated_score": final_score
        },
        "ai_threat_analysis": {
            "detailed_explanation": explanation,
            "mitigation_recommendations": recommendations
        },
        "preprocessing_metrics": preprocessed_data,
        "security_analysis_modules": {
            "module_3_1_sensitive_data": m31_sensitive,
            "module_3_2_prompt_injection": m32_injection,
            "module_3_3_jailbreak_detection": m33_jailbreak,
            "module_3_4_privacy_compliance": m34_compliance,
            "module_3_5_contextual_analysis": m35_contextual
        }
    }
    
    return jsonify(response_payload)

if __name__ == '__main__':
    app.run(debug=True, port=5000)