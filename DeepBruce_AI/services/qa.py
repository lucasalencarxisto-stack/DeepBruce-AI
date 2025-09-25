# oqs_step3/services/qa.py
# Resposta extrativa simples: seleciona frases com maior sobreposição com a pergunta
from typing import List, Dict
import re, math
import networkx as nx

# Tenta importar do chunk.py; se falhar, usa um fallback local
try:
    from .chunk import split_sentences  # o ideal
except Exception:
    _SENT_SPLIT = re.compile(r"(?<=[.!?。！？])\s+|\n+")
    def split_sentences(text: str):
        text = (text or "").strip()
        if not text:
            return []
        return [p.strip() for p in _SENT_SPLIT.split(text) if p.strip()]

TOKEN = re.compile(r"\w+", re.UNICODE)

def _sent_score(a_tokens, b_tokens):
    a, b = set(a_tokens), set(b_tokens)
    inter = len(a & b)
    if inter == 0: return 0.0
    return inter / math.sqrt(len(a) * len(b))

def textrank_summary(text: str, max_sentences: int = 3) -> str:
    sents = split_sentences(text)
    if len(sents) <= max_sentences:
        return " ".join(sents)
    tokens = [[t.lower() for t in TOKEN.findall(s)] for s in sents]
    G = nx.Graph()
    G.add_nodes_from(range(len(sents)))
    for i in range(len(sents)):
        for j in range(i+1, len(sents)):
            w = _sent_score(tokens[i], tokens[j])
            if w > 0:
                G.add_edge(i, j, weight=w)
    scores = nx.pagerank(G, weight="weight")
    top = sorted(range(len(sents)), key=lambda i: scores.get(i, 0), reverse=True)[:max_sentences]
    top.sort()
    return " ".join(sents[i] for i in top)

def extractive_answer(question: str, context_items: List[Dict], max_sentences: int = 3) -> str:
    text = " ".join(item.get("document", "") for item in context_items)
    if not text.strip():
        return "Não encontrei uma resposta direta no contexto disponível."
    return textrank_summary(text, max_sentences=max_sentences)
