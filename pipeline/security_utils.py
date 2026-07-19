"""Shared helpers for PromptX security-analysis modules."""

from __future__ import annotations


def mask_value(value: str, visible_prefix: int = 2, visible_suffix: int = 2) -> str:
    """Return evidence that is useful for review without exposing the secret."""
    value = str(value)
    if len(value) <= visible_prefix + visible_suffix:
        return "*" * len(value)
    return f"{value[:visible_prefix]}{'*' * max(4, len(value) - visible_prefix - visible_suffix)}{value[-visible_suffix:]}"


def severity_from_score(score: int) -> str:
    if score >= 30:
        return "Critical"
    if score >= 20:
        return "High"
    if score >= 10:
        return "Medium"
    if score > 0:
        return "Low"
    return "None"


def build_result(findings: list[dict], maximum_score: int) -> dict:
    """Create a consistent result payload for every security module."""
    score = min(sum(finding["score"] for finding in findings), maximum_score)
    return {
        "risk_detected": bool(findings),
        "findings": findings,
        "module_score": score,
        "severity": severity_from_score(score),
        "module_risk_contribution": severity_from_score(score),
    }
