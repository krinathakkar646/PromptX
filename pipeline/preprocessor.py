"""Prompt normalisation used before the security-analysis modules run."""

import spacy


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Avoid network downloads at application startup; the project still runs with a light fallback.
    nlp = spacy.blank("en")


def clean_and_tokenize(raw_prompt: str) -> dict:
    """Normalize prompt text and return privacy-preserving processing metrics."""
    normalized_text = " ".join(raw_prompt.strip().lower().split())
    doc = nlp(normalized_text)
    clean_tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return {
        "normalized_character_count": len(normalized_text),
        "clean_tokens": clean_tokens,
        "token_count": len(doc),
    }
