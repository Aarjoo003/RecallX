import re
from typing import Set, Tuple, List

# Conversational Hinglish abbreviations and colloquial spelling map
HINGLISH_ABBR = {
    # Common conversational & question markers requested
    "bday": "birthday",
    "bd": "birthday",
    "b'day": "birthday",
    "b-day": "birthday",
    "janamdin": "birthday",
    "kab": "when",
    "kaha": "where",
    "kidhar": "where",
    "ka": "of",
    "ki": "of",
    "ke": "of",
    "mera": "my",
    "meri": "my",
    "mere": "my",
    "hum": "we",
    "humara": "our",
    "hume": "us",
    "hua": "happened",
    "huye": "happened",
    "kr": "kar",
    "krna": "karna",
    "kya": "what",
    "paise": "money",
    "paisa": "money",
    "btw": "by the way",
    "pls": "please",
    "plz": "please",
    "thx": "thanks",
    "thnx": "thanks",
    "thnks": "thanks",
    "h": "hai",
    "fnl": "final",
    "krdio": "kar dena",
    "prso": "parso",
    "projct": "project",
    "assignmnt": "assignment",
    "clg": "college",
    "btado": "bata do",
    "bje": "baje",
    "bta": "bata",
    "bataya": "bataya",
    "rha": "raha",
    "ni": "nahi",
    "yr": "yaar",
    "kharche": "expenses",
    "kharcha": "expense",
    "kahan": "where",
    "kaha": "where",
    "kb": "kab",
    "attn": "attendance",
}

# Semantic dictionary to map conversational Hinglish into English equivalents for dual vector search
HINGLISH_TO_ENGLISH = {
    "bday": "birthday",
    "birthday": "birthday",
    "janamdin": "birthday",
    "kab": "when",
    "kb": "when",
    "kaha": "where",
    "kahan": "where",
    "kharche": "expenses",
    "kharcha": "expense",
    "kidhar": "where",
    "mera": "my",
    "meri": "my",
    "mere": "my",
    "hum": "we",
    "humara": "our",
    "hua": "happened",
    "kya": "what",
    "paise": "money",
    "paisa": "budget money",
    "date": "date",
    "tarikh": "date",
    "din": "day",
    "bataya": "told mentioned",
    "bola": "said stated",
    "tha": "was",
    "thi": "was",
    "hai": "is",
    "h": "is",
    "jaane": "going",
    "wale": "planning",
    "the": "were",
    "decide": "decided finalized",
    "final": "finalized locked",
    "bare": "about",
    "me": "in about",
    "baat": "discussed talked",
    "hui": "happened discussed",
}

def tokenize(text: str) -> List[str]:
    """Extract lowercase alphanumeric tokens."""
    if not text:
        return []
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

def normalize_text(text: str) -> str:
    """Normalize Hinglish, typos, and abbreviations for enhanced retrieval."""
    if not text:
        return ""
    words = text.split()
    normalized = []
    for w in words:
        clean = re.sub(r"[^\w\s']", "", w).lower()
        if clean in HINGLISH_ABBR:
            normalized.append(HINGLISH_ABBR[clean])
        else:
            normalized.append(w)
    return " ".join(normalized)

def translate_hinglish_to_semantic_english(text: str) -> str:
    """
    Translates key conversational Hinglish tokens into English semantic equivalents.
    Useful for bridging vocabulary gaps when querying sentence-transformer dense vectors.
    """
    if not text:
        return ""
    tokens = tokenize(text)
    translated = []
    for tok in tokens:
        if tok in HINGLISH_TO_ENGLISH:
            translated.append(HINGLISH_TO_ENGLISH[tok])
        else:
            translated.append(tok)
    return " ".join(translated)

def compute_word_overlap(query: str, text: str) -> Tuple[int, Set[str]]:
    """Compute exact token overlap between query and text, excluding conversational stopwords."""
    STOPWORDS = {
        "is", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with",
        "hai", "h", "ka", "ki", "ke", "ko", "me", "mein", "se", "ne", "tha", "thi", "the",
        "kya", "bhai", "yaar", "yr", "na", "to", "bhi"
    }
    q_tokens = set(tokenize(query)) - STOPWORDS
    t_tokens = set(tokenize(text)) - STOPWORDS
    overlap = q_tokens & t_tokens
    return len(overlap), overlap

