import re
from typing import Dict, List, Tuple

OPERATORS = {"AND", "OR", "NOT"}
PRECEDENCE = {"NOT": 3, "AND": 2, "OR": 1}
RIGHT_ASSOCIATIVE = {"NOT"}

class QueryError(ValueError):
    pass

def tokenize_query(query: str) -> List[str]:
    """Tokenize words, parentheses, and Boolean operators (case-insensitive)."""
    tokens = re.findall(r"\(|\)|[A-Za-z0-9_]+", query)
    if not tokens:
        return []
    return [tok.upper() if tok.upper() in OPERATORS else tok.lower() for tok in tokens]

def infix_to_postfix(query: str) -> Tuple[List[str], List[str]]:
    """Validate and convert an infix Boolean query to postfix using shunting-yard."""
    tokens = tokenize_query(query)
    if not tokens:
        raise QueryError("Empty query. Enter a term or Boolean expression.")

    output: List[str] = []
    stack: List[str] = []
    expect_operand = True

    for token in tokens:
        if token == "(":
            if not expect_operand:
                raise QueryError("Missing operator before '('.")
            stack.append(token)
            expect_operand = True
        elif token == ")":
            if expect_operand:
                raise QueryError("Unexpected ')' or missing term/operator.")
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if not stack:
                raise QueryError("Mismatched parentheses: missing '('.")
            stack.pop()
            expect_operand = False
        elif token in OPERATORS:
            if token == "NOT":
                if not expect_operand:
                    raise QueryError("NOT must appear before a term or parenthesized expression.")
                while (stack and stack[-1] in OPERATORS and
                       (PRECEDENCE[stack[-1]] > PRECEDENCE[token] or
                        (PRECEDENCE[stack[-1]] == PRECEDENCE[token] and token not in RIGHT_ASSOCIATIVE))):
                    output.append(stack.pop())
                stack.append(token)
                expect_operand = True
            else:
                if expect_operand:
                    raise QueryError(f"Operator {token} is missing a left operand.")
                while (stack and stack[-1] in OPERATORS and
                       (PRECEDENCE[stack[-1]] > PRECEDENCE[token] or
                        (PRECEDENCE[stack[-1]] == PRECEDENCE[token] and token not in RIGHT_ASSOCIATIVE))):
                    output.append(stack.pop())
                stack.append(token)
                expect_operand = True
        else:
            if not expect_operand:
                raise QueryError(f"Missing Boolean operator before '{token}'.")
            output.append(token)
            expect_operand = False

    if expect_operand:
        raise QueryError("Query ends with an operator or incomplete expression.")
    while stack:
        top = stack.pop()
        if top == "(":
            raise QueryError("Mismatched parentheses: missing ')'.")
        output.append(top)

    # Postfix validation catches malformed operator/operand combinations.
    depth = 0
    for token in output:
        if token == "NOT":
            if depth < 1:
                raise QueryError("NOT has no operand.")
        elif token in {"AND", "OR"}:
            if depth < 2:
                raise QueryError(f"{token} requires two operands.")
            depth -= 1
        else:
            depth += 1
    if depth != 1:
        raise QueryError("Malformed Boolean expression.")
    return tokens, output

def postings_intersection(left: List[str], right: List[str]) -> List[str]:
    """Intersect sorted postings in O(m+n) time using two pointers."""
    i = j = 0
    result = []
    while i < len(left) and j < len(right):
        if left[i] == right[j]:
            result.append(left[i]); i += 1; j += 1
        elif left[i] < right[j]:
            i += 1
        else:
            j += 1
    return result

def postings_union(left: List[str], right: List[str]) -> List[str]:
    """Union sorted postings in O(m+n) time, without duplicates."""
    i = j = 0
    result = []
    while i < len(left) and j < len(right):
        if left[i] == right[j]:
            result.append(left[i]); i += 1; j += 1
        elif left[i] < right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def postings_complement(postings: List[str], universe: List[str]) -> List[str]:
    """Return universe minus postings in O(U+P) time using two pointers."""
    i = j = 0
    result = []
    while i < len(universe):
        if j >= len(postings) or universe[i] < postings[j]:
            result.append(universe[i]); i += 1
        elif universe[i] == postings[j]:
            i += 1; j += 1
        else:
            j += 1
    return result

class BooleanSearchEngine:
    def __init__(self, inverted_index: Dict[str, List[str]], all_doc_ids: List[str], use_stemming: bool = False):
        self.index = {term: sorted(postings) for term, postings in inverted_index.items()}
        self.universe = sorted(all_doc_ids)
        self.use_stemming = use_stemming
        self._stemmer = None
        if use_stemming:
            try:
                from nltk.stem import PorterStemmer
                self._stemmer = PorterStemmer()
            except ImportError:
                raise RuntimeError("Porter stemming requires NLTK. Install it with: pip install nltk")

    def search(self, query: str):
        tokens, postfix = infix_to_postfix(query)
        if self.use_stemming:
            postfix = [self._stemmer.stem(token) if token not in OPERATORS else token for token in postfix]
        stack: List[List[str]] = []
        for token in postfix:
            if token == "NOT":
                operand = stack.pop()
                stack.append(postings_complement(operand, self.universe))
            elif token == "AND":
                right = stack.pop(); left = stack.pop()
                stack.append(postings_intersection(left, right))
            elif token == "OR":
                right = stack.pop(); left = stack.pop()
                stack.append(postings_union(left, right))
            else:
                # Unknown terms correctly map to an empty postings list.
                stack.append(self.index.get(token, []))
        return tokens, postfix, stack[0]
