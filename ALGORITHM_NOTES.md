# Algorithm Notes for Viva

## Preprocessing
1. Lowercase the source text.
2. Tokenize with a regular expression.
3. Remove common stopwords.
4. Optionally apply the Porter stemming algorithm (NLTK PorterStemmer).

## Inverted index
For each document, preprocess title + abstract. For every distinct term, append the document ID. Sort each postings list.

## Shunting-yard parser
- Operands go directly to output.
- Operators are placed on a stack according to precedence.
- Parentheses control operator popping.
- Final output is postfix, which is easy to evaluate with a stack.

## Postings algorithms
Intersection advances the pointer with the smaller current ID and emits equal IDs.
Union emits the smaller current ID and emits equal IDs once.
Complement scans the complete sorted document universe and skips IDs present in the term postings.

## Why sorted postings?
Sorted postings enable linear-time merge operations. For postings lengths m and n, intersection and union take O(m+n) time.

## Evaluation metrics
Precision = relevant retrieved / all retrieved.
Recall = relevant retrieved / all relevant.
The test file includes manual relevance sets for five queries. These are illustrative judgments for this local demonstration collection.
