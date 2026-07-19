from flask import Flask, request, jsonify, render_template
from pipeline.preprocessor import clean_and_tokenize
from pipeline.sensitive_data import redact_sensitive_data, scan_sensitive_data
from pipeline.prompt_injection import scan_prompt_injection
from pipeline.jailbreak import scan_jailbreak
from pipeline.privacy_compliance import scan_privacy_compliance
from pipeline.contextual_analysis import scan_contextual_analysis
from pipeline.logger import get_recent_logs, init_db, log_incident

app = Flask(__name__)

# Initialize the SQLite database on startup
init_db()

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/api/history', methods=['GET'])
def scan_history():
    """Expose only redacted local records for the dashboard history panel."""
    return jsonify({"logs": get_recent_logs()})

@app.route('/api/analyze', methods=['POST'])
def analyze_prompt():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400
    
    user_prompt = data['prompt']
    
    # 1. Run text cleaning preprocessing (Step 2)
    preprocessed_data = clean_and_tokenize(user_prompt)
    
    # 2. Core security screening (each module returns a score and severity)
    m31_sensitive = scan_sensitive_data(user_prompt)
    m32_injection = scan_prompt_injection(user_prompt)
    m33_jailbreak = scan_jailbreak(user_prompt)
    m34_compliance = scan_privacy_compliance(user_prompt)
    m35_contextual = scan_contextual_analysis(user_prompt)
    
    # 3. Severity-weighted scoring with an additional combined-attack penalty.
    module_results = [
        ("Sensitive Data Leakage", m31_sensitive),
        ("Prompt Injection Attack", m32_injection),
        ("Adversarial Jailbreak Attempt", m33_jailbreak),
        ("Compliance Policy Breach", m34_compliance),
        ("Risky Semantic Context", m35_contextual),
    ]
    triggered_modules = [name for name, result in module_results if result["risk_detected"]]
    base_score = sum(result["module_score"] for _, result in module_results)
    combined_attack_bonus = 0
    if len(triggered_modules) >= 2:
        combined_attack_bonus += 10
    if len(triggered_modules) >= 3:
        combined_attack_bonus += 5
    final_score = min(base_score + combined_attack_bonus, 100)
    
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
            recommendations.append("Action: Remove or obtain approval for protected personal data, payment identifiers, or confidential information.")
        if len(triggered_modules) >= 2:
            recommendations.append("Action: Treat this as a combined attack and escalate it for security review.")

    # 4. Log only a redacted version of the prompt to avoid creating a second data leak.
    log_incident(
        raw_prompt=redact_sensitive_data(user_prompt),
        status=final_status,
        risk_score=final_score,
        risk_classification=risk_class
    )
    
    # Construct complete unified report payload
    response_payload = {
        "status": final_status,
        "risk_classification": risk_class,
        "risk_scoring_engine": {
            "calculated_score": final_score,
            "base_score": base_score,
            "combined_attack_bonus": combined_attack_bonus,
            "triggered_module_count": len(triggered_modules),
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
