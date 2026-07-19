import spacy

# Fixed the syntax error here (changed ) to :)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def clean_and_tokenize(raw_prompt: str) -> dict:
    """
    Cleans, tokenizes, and normalizes the input prompt text.
    Strips out stop words and provides structural insights.
    """
    # 1. Lowercase normalization
    normalized_text = raw_prompt.strip().lower()
    
    # 2. Process text through spaCy
    doc = nlp(normalized_text)
    
    # 3. Tokenization & Stop word removal
    clean_tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    
    return {
        "original_text": raw_prompt,
        "clean_tokens": clean_tokens,
        "token_count": len(doc)
    }