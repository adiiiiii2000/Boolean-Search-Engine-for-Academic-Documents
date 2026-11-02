import json
from collections import defaultdict
from pathlib import Path
from preprocessing import preprocess

DEFAULT_DATA = Path(__file__).parent / "data" / "academic_documents.json"

def load_documents(path=DEFAULT_DATA):
    with open(path, "r", encoding="utf-8") as f:
        docs = json.load(f)
    return docs

def build_inverted_index(documents, use_stemming=False):
    """Return term -> sorted list of document IDs."""
    index = defaultdict(list)
    for doc in documents:
        text = doc["title"] + " " + doc["abstract"]
        for term in set(preprocess(text, use_stemming)):
            index[term].append(doc["doc_id"])
    return {term: sorted(ids) for term, ids in sorted(index.items())}

def build_incidence_matrix(index, doc_ids, terms=None):
    """Return rows (term, [0/1...]) for a selected term vocabulary."""
    terms = sorted(terms if terms is not None else index.keys())
    rows = []
    for term in terms:
        postings = index.get(term, [])
        row = [1 if doc_id in postings else 0 for doc_id in doc_ids]
        rows.append((term, row))
    return rows
