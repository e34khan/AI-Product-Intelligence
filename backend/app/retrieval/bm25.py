import math
import re
from collections import Counter

from app.db.models import Chunk

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")  # splits text into lowercase word/number chunks

K1 = 1.5  # controls how fast repeated term occurrences stop adding extra score
B = 0.75  # controls how strongly longer documents get penalized, 0 = no penalty, 1 = full


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


class BM25Index:
    def __init__(self, chunks: list[tuple[int, int, str]]):
        # each entry is (chunk_id, product_id, text). keeping product_id here lets
        # search() filter to one product without a separate database round trip
        self.chunk_ids = [c[0] for c in chunks]
        self.product_ids = [c[1] for c in chunks]
        self.text_by_id = {c[0]: c[2] for c in chunks}

        self.doc_tokens = [tokenize(c[2]) for c in chunks]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths)
        self.doc_term_counts = [Counter(tokens) for tokens in self.doc_tokens]
        self.num_docs = len(chunks)

        # document frequency: how many chunks each term appears in at least once.
        # computed once over the whole corpus, independent of any later product filter,
        # since rarity is a property of the whole collection, not just one product's reviews
        df = Counter()
        for tokens in self.doc_tokens:
            for term in set(tokens):
                df[term] += 1
        self.doc_freq = df

    def _idf(self, term: str) -> float:
        n = self.doc_freq.get(term, 0)
        return math.log((self.num_docs - n + 0.5) / (n + 0.5) + 1)

    def _score(self, query_terms: list[str], doc_index: int) -> float:
        term_counts = self.doc_term_counts[doc_index]
        doc_length = self.doc_lengths[doc_index]

        total = 0.0
        for term in query_terms:
            f = term_counts.get(term, 0)
            if f == 0:
                continue  # term never appears in this chunk, contributes nothing

            numerator = f * (K1 + 1)
            denominator = f + K1 * (1 - B + B * doc_length / self.avg_doc_length)
            total += self._idf(term) * (numerator / denominator)

        return total

    def search(self, query: str, k: int = 5, product_id: int | None = None) -> list[tuple[int, float]]:
        query_terms = tokenize(query)

        scored = []
        for i in range(self.num_docs):
            if product_id is not None and self.product_ids[i] != product_id:
                continue
            scored.append((self.chunk_ids[i], self._score(query_terms, i)))

        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]


def build_index(session) -> BM25Index:
    # querying specific columns instead of whole Chunk objects, since that's all
    # the index needs and it avoids pulling embedding vectors along for the ride
    chunks = session.query(Chunk.id, Chunk.product_id, Chunk.text).all()
    return BM25Index(chunks)
