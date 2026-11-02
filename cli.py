import argparse
from indexer import load_documents, build_inverted_index
from boolean_engine import BooleanSearchEngine, QueryError

def main():
    parser = argparse.ArgumentParser(description="Boolean Academic Document Search (CLI)")
    parser.add_argument("query", nargs="*", help='Boolean query, e.g. "AI AND Security"')
    parser.add_argument("--stem", action="store_true", help="Enable optional Porter stemming")
    args = parser.parse_args()

    docs = load_documents()
    index = build_inverted_index(docs, args.stem)
    engine = BooleanSearchEngine(index, [d["doc_id"] for d in docs], use_stemming=args.stem)
    query = " ".join(args.query)
    if not query:
        query = input("Enter Boolean query (AND/OR/NOT): ").strip()
    try:
        tokens, postfix, results = engine.search(query)
        by_id = {d["doc_id"]: d for d in docs}
        print("Tokens: ", tokens)
        print("Postfix:", " ".join(postfix))
        print(f"Retrieved {len(results)} document(s):")
        for doc_id in results:
            print(f"- {doc_id}: {by_id[doc_id]['title']}")
    except QueryError as exc:
        print(f"Query error: {exc}")

if __name__ == "__main__":
    main()
