"""Functional test suite: expected results and manually judged relevance.
Run from project root: python tests/test_queries.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from indexer import load_documents, build_inverted_index
from boolean_engine import BooleanSearchEngine, QueryError

docs = load_documents()
index = build_inverted_index(docs)
engine = BooleanSearchEngine(index, [d["doc_id"] for d in docs])
by_id = {d["doc_id"]: d for d in docs}
universe = set(by_id)

cases = [
    ("retrieval", {"D001","D002","D003","D004","D005","D007","D009","D010","D050"}),
    ("machine AND learning", {"D011","D015","D017","D020","D026","D044","D048"}),
    ("blockchain OR database", {"D031","D032","D033","D034","D035","D037","D038"}),
    ("NOT blockchain", universe - {"D033","D035","D038"}),
    ("(machine OR neural) AND learning", {"D011","D013","D015","D017","D020","D026","D044","D048"}),
    ("network AND security", {"D045","D046"}),
    ("machine AND NOT neural", {"D011","D015","D017","D020","D026","D044","D048"}),
    ("quantum", set()),
    ("retrieval OR tokenization", {"D001","D002","D003","D004","D005","D007","D009","D010","D047","D050"}),
    ("AI AND security", {"D026"}),
    ("(database OR information) AND NOT network", {"D002","D003","D005","D007","D010","D027","D030","D031","D032","D034","D037","D038","D049","D050"}),
]

# Manual relevance judgments: these may include conceptually relevant documents
# that exact Boolean matching does not retrieve, making precision/recall informative.
judged = {
    "retrieval": {"D001","D002","D003","D004","D005","D006","D007","D008","D009","D010","D050"},
    "machine AND learning": {"D011","D013","D015","D016","D017","D019","D020","D026","D044","D048"},
    "blockchain OR database": {"D031","D032","D033","D034","D035","D036","D037","D038","D039"},
    "network AND security": {"D021","D022","D023","D025","D027","D028","D045","D046"},
    "AI AND security": {"D020","D026"},
}

def metrics(retrieved, relevant):
    relevant_retrieved = len(retrieved & relevant)
    precision = relevant_retrieved / len(retrieved) if retrieved else 0.0
    recall = relevant_retrieved / len(relevant) if relevant else 0.0
    return precision, recall

print("BOOLEAN SEARCH ENGINE TEST REPORT")
print("=" * 88)
passed = 0
for query, expected in cases:
    tokens, postfix, actual_list = engine.search(query)
    actual = set(actual_list)
    ok = actual == expected
    passed += int(ok)
    print(f"\nQUERY: {query}")
    print(f"POSTFIX: {' '.join(postfix)}")
    print(f"EXPECTED IDs: {', '.join(sorted(expected)) or '(none)'}")
    print(f"ACTUAL IDs:   {', '.join(sorted(actual)) or '(none)'}")
    print("STATUS:", "PASS" if ok else "FAIL")
    if query in judged:
        precision, recall = metrics(actual, judged[query])
        print(f"MANUALLY JUDGED RELEVANT: {len(judged[query])}")
        print(f"PRECISION: {precision:.3f} | RECALL: {recall:.3f}")
    print("TITLES:")
    for doc_id in sorted(actual):
        print(f"  {doc_id}: {by_id[doc_id]['title']}")

print("\nINVALID / EDGE CASE TESTS")
print("=" * 88)
for query in ["", "(AI AND security", "AI OR", "AND AI", "AI security", "AI AND ()"]:
    try:
        engine.search(query)
        print(f"QUERY: {query!r} -> FAIL (expected QueryError)")
    except QueryError as exc:
        passed += 1
        print(f"QUERY: {query!r} -> PASS ({exc})")

lower_ok = engine.search("ai and security")[2] == engine.search("AI AND SECURITY")[2]
passed += int(lower_ok)
print(f"\nLowercase operators: {'PASS' if lower_ok else 'FAIL'}")
print(f"\nSUMMARY: {passed} checks passed out of {len(cases) + 7}.")
