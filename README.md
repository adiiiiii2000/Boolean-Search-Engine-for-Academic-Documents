# Boolean Search Engine for Academic Documents


## Implemented requirements
- 50 offline academic-style documents (title + abstract), stored in JSON and CSV.
- Preprocessing: lowercase, tokenization, stopword removal, optional NLTK Porter stemming.
- Inverted index: term → sorted document-ID postings.
- Term-document incidence matrix for demonstration.
- Boolean query parser using shunting-yard conversion to postfix.
- Query operators `AND`, `OR`, `NOT`, parentheses; precedence `NOT > AND > OR`.
- Postings-list intersection, union, and complement implemented with two-pointer merge algorithms (no Python set operations in query evaluation).
- Streamlit UI with parsed tokens/postfix, result count, document titles/snippets, highlighted query terms, index statistics, preprocessing demo, index and incidence matrix.
- CLI fallback and test suite with expected-vs-actual retrieval, manual relevance judgments, precision and recall.

## Install and run (Windows PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```
Open http://localhost:8501.

If activation is blocked:
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m streamlit run app.py
```

## CLI fallback
```powershell
python cli.py "AI AND cybersecurity"
python cli.py "(machine OR neural) AND learning"
python cli.py "NOT blockchain"
python cli.py --stem "retrieval AND documents"
```

## Run the test suite
```powershell
python tests/test_queries.py
```
The test script prints expected and actual document IDs, titles, pass/fail status, and precision/recall for five manually judged queries. The relevance judgments are illustrative and documented in the script; adapt them if your instructor supplies a different relevance standard.

## Boolean query syntax
- `AI AND security`
- `blockchain OR database`
- `NOT malware`
- `(machine OR neural) AND learning`

Operators are case-insensitive. Terms are exact tokens after preprocessing. Unknown terms return an empty postings list. Explicit operators are required between terms.

## Algorithm and complexity
Let `m` and `n` be the lengths of two sorted postings lists and `U` the number of documents:
- Intersection: O(m+n), two-pointer merge.
- Union: O(m+n), two-pointer merge.
- Complement: O(U+p), where `p` is the postings length, by scanning the sorted universe and postings.
- Query parsing: O(q), where `q` is the number of query tokens.
- Query evaluation: each Boolean merge is linear in the lengths of its input postings.

The parser uses shunting-yard conversion to postfix. The evaluator uses a stack and custom postings-list merge functions. It does not use Python set shortcuts for Boolean evaluation.

## Dataset note
The 50 records are original short academic-style demonstration documents written for this project. They are not claimed to be published papers. The dataset is bundled locally; no network or dataset download is required.

## Optional Porter stemming
The UI includes a Porter stemming toggle. NLTK's PorterStemmer is algorithmic and does not download a corpus. If NLTK is unavailable, install dependencies using `pip install -r requirements.txt`.
