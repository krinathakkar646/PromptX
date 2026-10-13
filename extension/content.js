(function () {
  "use strict";

  const API_URL = "http://127.0.0.1:5000/api/analyze";
  const HIGH_RISK_SCORE = 50;
  const DASHBOARD_URL = "http://127.0.0.1:5000/?prompt=";
  let lastPrompt = "";
  let lastResult = null;
  let scanInProgress = false;

  function getInput() {
    const active = document.activeElement;
    if (active && (active.tagName === "TEXTAREA" || active.isContentEditable)) {
      return active;
    }
    return document.querySelector("textarea") ||
      document.querySelector("[contenteditable='true']");
  }

  function readPrompt(input) {
    return input.tagName === "TEXTAREA" ? input.value.trim() : input.innerText.trim();
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (character) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    }[character]));
  }

  function getFindings(result) {
    return Object.values(result.security_analysis_modules || {})
      .filter((item) => item && item.risk_detected)
      .map((item) => ({
        name: item.threat_type || item.module_name || "Security finding",
        evidence: item.matched_phrase || item.matched_value ||
          item.matched_indicator || item.matched_signature || "Suspicious pattern detected"
      }));
  }

  function getImpact(score, findings) {
    const names = findings.map((finding) => finding.name.toLowerCase()).join(" ");
    const risks = [];
    if (names.includes("sensitive") || names.includes("privacy") || names.includes("compliance")) {
      risks.push("Credentials, personal data, payment information, or confidential business data may be exposed.");
    }
    if (names.includes("injection") || names.includes("jailbreak")) {
      risks.push("The prompt may manipulate the model into ignoring its instructions or producing unsafe output.");
    }
    if (score >= HIGH_RISK_SCORE) {
      risks.push("Submitting it without review could cause data leakage, policy violations, or an unsafe downstream action.");
    }
    return risks.length ? risks : ["No immediate security impact was identified by the configured checks."];
  }

  function createPanel() {
    let panel = document.getElementById("promptx-safety-panel");
    if (panel) return panel;
    panel = document.createElement("div");
    panel.id = "promptx-safety-panel";
    panel.innerHTML = `
      <div class="promptx-header">
        <strong>PromptX Safety Check</strong>
        <button type="button" aria-label="Close">×</button>
      </div>
      <div class="promptx-body">Enter a prompt to scan it.</div>
    `;
    document.body.appendChild(panel);
    panel.querySelector("button").addEventListener("click", () => panel.remove());
    return panel;
  }

  function showResult(result) {
    const panel = createPanel();
    const score = result.risk_scoring_engine.calculated_score;
    const classification = result.risk_classification;
    const findings = getFindings(result);
    const colour = score >= HIGH_RISK_SCORE ? "#b42318" : score > 0 ? "#b54708" : "#027a48";
    const impacts = getImpact(score, findings);
    panel.querySelector(".promptx-body").innerHTML = `
      <div class="promptx-score" style="color:${colour}">${classification} · ${score}/100</div>
      <section class="promptx-detail-block">
        <strong>Detected attack or risk</strong>
        <ul>${findings.length
          ? findings.map((finding) => `<li><b>${escapeHtml(finding.name)}</b><br><small>Evidence: ${escapeHtml(finding.evidence)}</small></li>`).join("")
          : "<li>No security issues detected.</li>"}</ul>
      </section>
      <section class="promptx-detail-block">
        <strong>Information at risk</strong>
        <div>${escapeHtml(findings.length ? findings.map((finding) => finding.name).join(", ") : "None detected")}</div>
      </section>
      <section class="promptx-detail-block">
        <strong>Possible impact</strong>
        <ul>${impacts.map((impact) => `<li>${escapeHtml(impact)}</li>`).join("")}</ul>
      </section>
      ${score >= HIGH_RISK_SCORE
        ? `<div class="promptx-warning">This prompt has a high risk score. Review it before sending.</div>`
        : ""}
      <div class="promptx-actions">
        <button type="button" class="promptx-details">View full details</button>
        ${score > 0 ? `<button type="button" class="promptx-confirm">Send anyway</button>` : ""}
      </div>
    `;
    panel.querySelector(".promptx-details")?.addEventListener("click", () => {
      window.open(`${DASHBOARD_URL}${encodeURIComponent(lastPrompt)}`, "_blank", "noopener");
    });
    panel.querySelector(".promptx-confirm")?.addEventListener("click", () => {
      lastResult = { ...result, confirmed: true };
      panel.remove();
      const input = getInput();
      input?.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", code: "Enter", bubbles: true }));
    });
  }

  async function scan(input) {
    const prompt = readPrompt(input);
    if (!prompt || scanInProgress) return;
    scanInProgress = true;
    const panel = createPanel();
    panel.querySelector(".promptx-body").textContent = "Scanning with local PromptX API...";
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      const result = await response.json();
      lastPrompt = prompt;
      lastResult = result;
      showResult(result);
    } catch (error) {
      panel.querySelector(".promptx-body").textContent =
        "PromptX API is unavailable. Start the Flask server before sending.";
    } finally {
      scanInProgress = false;
    }
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" || event.shiftKey || event.isComposing) return;
    const input = getInput();
    if (!input || !readPrompt(input)) return;
    const prompt = readPrompt(input);
    if (lastPrompt === prompt && lastResult?.confirmed) {
      lastPrompt = "";
      lastResult = null;
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
    scan(input);
  }, true);

  const style = document.createElement("style");
  style.textContent = `
    #promptx-safety-panel { position:fixed; right:20px; bottom:20px; z-index:2147483647;
      width:360px; max-height:80vh; overflow:auto; color:#172033; background:#fff; border:1px solid #d0d5dd;
      border-radius:12px; box-shadow:0 8px 28px #0003; font:14px Arial,sans-serif; }
    .promptx-header { display:flex; justify-content:space-between; align-items:center;
      padding:12px 14px; background:#172033; color:#fff; border-radius:12px 12px 0 0; }
    .promptx-header button { border:0; background:transparent; color:#fff; font-size:20px; cursor:pointer; }
    .promptx-body { padding:14px; line-height:1.45; }
    .promptx-score { font-size:18px; font-weight:700; margin-bottom:8px; }
    .promptx-detail-block { margin-top:12px; padding-top:8px; border-top:1px solid #eaecf0; }
    .promptx-detail-block ul { margin:6px 0 0; padding-left:20px; }
    .promptx-detail-block li { margin:5px 0; }
    .promptx-detail-block small { color:#667085; overflow-wrap:anywhere; }
    .promptx-warning { margin-top:12px; padding:9px; background:#fff3cd; border-radius:6px; }
    .promptx-actions { display:flex; gap:8px; margin-top:12px; }
    .promptx-actions button { padding:8px 10px; border:0; border-radius:6px; cursor:pointer; }
    .promptx-details { color:#172033; background:#e0eaff; }
    .promptx-confirm { color:#fff; background:#b42318;
    }
  `;
  document.documentElement.appendChild(style);
})();
