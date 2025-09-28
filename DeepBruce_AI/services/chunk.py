# BM25 + (opcional) TF-IDF re-rank com cache por namespace
from typing import List, Dict
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

TOKEN = re.compile(r"\w+", re.UNICODE)

_SENT_SPLIT = re.compile(r"(?<=[.!?。！？])\s+|\n+")


class Retriever:
    def __init__(self, store):
        self.store = store
        self._cache = {}  # namespace -> {"rows": rows, "bm25": bm25, "tokens": tokens}

    def _tokenize(self, s: str):
        return [t.lower() for t in TOKEN.findall(s)]

    def invalidate(self, namespace: str):
        self._cache.pop(namespace, None)

    def _ensure_index(self, namespace: str):
        if namespace in self._cache:
            return
        rows = self.store.fetch_namespace(namespace)
        corpus = [r["text"] for r in rows]
        tokens = [self._tokenize(c) for c in corpus]
        bm25 = BM25Okapi(tokens) if tokens else None
        self._cache[namespace] = {"rows": rows, "bm25": bm25, "tokens": tokens}

    def search(self, namespace: str, query: str, top_k: int = 5) -> List[Dict]:
        self._ensure_index(namespace)
        entry = self._cache.get(namespace, {})
        rows, bm25 = entry.get("rows", []), entry.get("bm25")

        if not rows or bm25 is None:
            return []

        scores = bm25.get_scores(self._tokenize(query))
        idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:max(top_k*3, top_k)]
        candidates = [rows[i] for i in idxs]

        texts = [c["text"] for c in candidates]
        vec = TfidfVectorizer(ngram_range=(1,2), min_df=1).fit(texts + [query])
        qv = vec.transform([query])
        M = vec.transform(texts)
        cos = cosine_similarity(qv, M)[0]
        order = sorted(range(len(cos)), key=lambda i: cos[i], reverse=True)[:top_k]
        ranked = [candidates[i] for i in order]

        out = []
        for r,i in zip(ranked, order):
            out.append({
                "id": r["id"],
                "document": r["text"],
                "metadata": r["meta"],
                "score": float(cos[i])
            })
        return out

def split_sentences(text: str):
    """
    Divide um texto em frases curtas para o TextRank do qa.py.
    Retorna lista de strings (frases).
    """
    text = (text or "").strip()
    if not text:
        return []
    return [p.strip() for p in _SENT_SPLIT.split(text) if p.strip()]