import re

def remove_duplicates(text):
    """Remove duplicate paragraphs by normalizing spaces and removing repeats."""
    paragraphs = list(dict.fromkeys(re.sub(r'\s+', ' ', text).split(". ")))  # Normalize spaces & split sentences
    return ". ".join(paragraphs)


def truncate_text(text, limit=3000):
    """Truncate text at the nearest sentence boundary before the limit."""
    if len(text) <= limit:
        return text
    # Find the last period (.) before limit and cut there
    last_sentence_end = text[:limit].rfind(". ")
    return text[:last_sentence_end+1] if last_sentence_end != -1 else text[:limit]

def clean_text(text):
    """Remove citation numbers like [4], [5]"""
    return re.sub(r"\[\d+\]", "", text)

def clean_irrelevant_content(text):
    """Remove irrelevant sections like newsletter & policy text."""
    stop_phrases = ["Newsletter", "Privacy Policy", "Terms of Service", "Sign In", "Founder first", "Start your day"]
    for phrase in stop_phrases:
        text = text.split(phrase)[0]  
    return text.strip()