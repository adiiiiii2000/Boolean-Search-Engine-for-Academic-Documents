import re
from typing import List

# A compact built-in stopword list keeps preprocessing fully offline.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "into", "is", "it", "of", "on", "or", "that", "the", "their",
    "this", "to", "using", "with", "while", "can", "also", "which"
}

def tokenize(text: str) -> List[str]:
    """Lowercase and tokenize alphabetic/numeric terms."""
    return re.findall(r"[a-z0-9]+", text.lower())

def preprocess(text: str, use_stemming: bool = False) -> List[str]:
    """Lowercase, tokenize, remove stopwords, and optionally Porter-stem.

    Porter stemming uses NLTK's bundled algorithm and does not download data.
    If NLTK is unavailable, the app reports this and continues without stemming.
    """
    terms = [term for term in tokenize(text) if term not in STOPWORDS]
    if use_stemming:
        try:
            from nltk.stem import PorterStemmer
            stemmer = PorterStemmer()
            terms = [stemmer.stem(term) for term in terms]
        except ImportError:
            raise RuntimeError("Porter stemming requires NLTK. Install it with: pip install nltk")
    return terms

def preprocessing_example(text: str, use_stemming: bool = False):
    return tokenize(text), preprocess(text, use_stemming)
