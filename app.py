import html
import re
import pandas as pd
import streamlit as st
from indexer import load_documents, build_inverted_index, build_incidence_matrix
from boolean_engine import BooleanSearchEngine, QueryError
from preprocessing import tokenize, preprocess

st.set_page_config(page_title="Boolean Academic Search", page_icon="🔎", layout="wide")
st.title("Boolean Search Engine for Academic Documents 🔎")

docs = load_documents()
doc_ids = sorted(d["doc_id"] for d in docs)
by_id = {d["doc_id"]: d for d in docs}

with st.sidebar:
    st.header("Index statistics")
    use_stemming = st.toggle("Enable Porter stemming (optional)", value=False)
    try:
        index = build_inverted_index(docs, use_stemming)
        stem_error = None
    except RuntimeError as exc:
        index = build_inverted_index(docs, False)
        stem_error = str(exc)
        st.warning(stem_error)
    engine = BooleanSearchEngine(index, doc_ids, use_stemming=use_stemming)
    st.metric("Documents", len(docs))
    st.metric("Vocabulary size", len(index))
    st.metric("Posting entries", sum(len(v) for v in index.values()))
    st.divider()
    st.markdown("**Operators**")
    st.markdown("- `AND`: intersection\n- `OR`: union\n- `NOT`: complement")
    st.caption("Precedence: NOT > AND > OR")

st.subheader("Search collection")
query = st.text_input("Boolean query", placeholder="(machine OR neural) AND learning")
search_col, help_col = st.columns([1, 3])
with search_col:
    run_search = st.button("Search", type="primary", use_container_width=True)
with help_col:
    st.caption("Use explicit operators and parentheses. Operators are case-insensitive.")

def highlight(text, terms):
    escaped = html.escape(text)
    terms = sorted({t for t in terms if t not in {"AND", "OR", "NOT"}}, key=len, reverse=True)
    if not terms:
        return escaped
    pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in terms) + r")\b", re.I)
    return pattern.sub(r'<mark>\1</mark>', escaped)

if run_search:
    try:
        tokens, postfix, results = engine.search(query)
        st.markdown(f"**Parsed tokens:** `{ ' '.join(tokens) }`")
        st.markdown(f"**Postfix expression:** `{ ' '.join(postfix) }`")
        st.metric("Result count", len(results))
        if results:
            for doc_id in results:
                doc = by_id[doc_id]
                st.markdown(f"### {doc['title']}  <small>({doc_id})</small>", unsafe_allow_html=True)
                snippet = doc["abstract"]
                st.markdown(highlight(snippet, tokens), unsafe_allow_html=True)
                st.divider()
        else:
            st.info("No documents matched this query.")
    except QueryError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Unexpected error: {exc}")

st.divider()
st.subheader("Preprocessing demonstration")
sample = st.text_area("Enter text to preprocess", "The Information Retrieval systems are searching documents with efficient indexes.")
raw_tokens = tokenize(sample)
try:
    processed = preprocess(sample, use_stemming)
    st.write("**Before (lowercase tokenization):**", ", ".join(raw_tokens))
    st.write("**After (stopword removal" + (", Porter stemming" if use_stemming else "") + "):**", ", ".join(processed))
except RuntimeError as exc:
    st.warning(str(exc))

st.divider()
st.subheader("Inverted index")
term_filter = st.text_input("Filter index terms", placeholder="e.g. retrieval")
filtered_terms = [t for t in sorted(index) if term_filter.lower() in t][:100]
if filtered_terms:
    index_rows = [{"Term": t, "Postings (Doc IDs)": ", ".join(index[t]), "DF": len(index[t])} for t in filtered_terms]
    st.dataframe(pd.DataFrame(index_rows), use_container_width=True, hide_index=True)
else:
    st.info("No matching index terms.")

st.subheader("Term-document incidence matrix")
matrix_terms = st.multiselect("Choose terms to display", options=sorted(index), default=[t for t in ["ai", "security", "retrieval", "machine"] if t in index])
if matrix_terms:
    matrix = build_incidence_matrix(index, doc_ids, matrix_terms)
    matrix_df = pd.DataFrame({term: row for term, row in matrix}, index=doc_ids).T
    st.dataframe(matrix_df, use_container_width=True)
else:
    st.caption("Select one or more terms to view their 0/1 incidence across documents.")

with st.expander("Document collection (all 50 records)"):
    st.dataframe(pd.DataFrame(docs), use_container_width=True, hide_index=True)

