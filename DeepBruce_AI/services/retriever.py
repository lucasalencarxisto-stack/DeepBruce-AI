import re
from typing import Any, Dict, List, Protocol

from nltk.stem.snowball import SnowballStemmer
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


_TOKEN = re.compile(r"\w+", re.UNICODE)
_STEMMER = SnowballStemmer("portuguese")


class NamespaceStore(Protocol):
    def fetch_namespace(
        self,
        namespace: str,
    ) -> List[Dict[str, Any]]:
        ...


def _normalize_scores(scores) -> List[float]:
    """
    Normaliza scores para o intervalo 0..1.
    """
    values = [float(score) for score in scores]

    if not values:
        return []

    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        if maximum > 0:
            return [1.0] * len(values)

        return [0.0] * len(values)

    return [
        (value - minimum) / (maximum - minimum)
        for value in values
    ]


def _token_set(text: str) -> set[str]:
    """
    Cria um conjunto simples de tokens para comparação
    de similaridade entre documentos.
    """
    return {
        token.lower()
        for token in _TOKEN.findall(text or "")
    }


def _jaccard_similarity(
    first: str,
    second: str,
) -> float:
    """
    Calcula similaridade entre dois textos usando Jaccard.
    """
    first_tokens = _token_set(first)
    second_tokens = _token_set(second)

    if not first_tokens or not second_tokens:
        return 0.0

    intersection = first_tokens & second_tokens
    union = first_tokens | second_tokens

    return len(intersection) / len(union)


class Retriever:
    """
    Retriever híbrido do pipeline RAG.

    Estratégia:

    1. BM25 recupera candidatos lexicalmente relevantes.
    2. TF-IDF por palavras analisa termos e bigramas.
    3. TF-IDF por caracteres ajuda com variações morfológicas.
    4. Os scores são combinados em um ranking híbrido.
    5. Chunks muito semelhantes são removidos.
    """

    def __init__(
        self,
        store: NamespaceStore,
        *,
        bm25_weight: float = 0.45,
        tfidf_weight: float = 0.55,
        candidate_multiplier: int = 4,
        duplicate_threshold: float = 0.90,
    ):
        if bm25_weight < 0 or tfidf_weight < 0:
            raise ValueError(
                "Os pesos do ranking não podem ser negativos."
            )

        total_weight = bm25_weight + tfidf_weight

        if total_weight <= 0:
            raise ValueError(
                "Ao menos um peso deve ser maior que zero."
            )

        if candidate_multiplier <= 0:
            raise ValueError(
                "candidate_multiplier deve ser maior que zero."
            )

        if not 0 <= duplicate_threshold <= 1:
            raise ValueError(
                "duplicate_threshold deve estar entre 0 e 1."
            )

        self.store = store

        # Normalizamos os pesos para sempre somarem 1.
        self.bm25_weight = bm25_weight / total_weight
        self.tfidf_weight = tfidf_weight / total_weight

        self.candidate_multiplier = candidate_multiplier
        self.duplicate_threshold = duplicate_threshold

        self._cache: Dict[str, Dict[str, Any]] = {}

    def _tokenize(
        self,
        text: str,
    ) -> List[str]:
        """
        Tokeniza e aplica stemming em português.

        Exemplo aproximado:

        criar
        criou
        criada

        passam a compartilhar uma raiz semelhante.
        """
        return [
            _STEMMER.stem(token.lower())
            for token in _TOKEN.findall(text or "")
        ]

    def invalidate(
        self,
        namespace: str,
    ) -> None:
        """
        Remove um namespace do cache.
        """
        self._cache.pop(namespace, None)

    def _ensure_index(
        self,
        namespace: str,
    ) -> None:
        """
        Cria o índice BM25 caso ainda não esteja em cache.
        """
        if namespace in self._cache:
            return

        rows = self.store.fetch_namespace(namespace)

        corpus = [
            row.get("text", "")
            for row in rows
        ]

        tokens = [
            self._tokenize(text)
            for text in corpus
        ]

        bm25 = (
            BM25Okapi(tokens)
            if tokens
            else None
        )

        self._cache[namespace] = {
            "rows": rows,
            "bm25": bm25,
        }

    def _remove_duplicates(
        self,
        results: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        Remove documentos quase duplicados do resultado final.
        """
        selected: List[Dict[str, Any]] = []

        for candidate in results:
            candidate_text = candidate["document"]

            duplicate = any(
                _jaccard_similarity(
                    candidate_text,
                    selected_item["document"],
                )
                >= self.duplicate_threshold
                for selected_item in selected
            )

            if duplicate:
                continue

            selected.append(candidate)

            if len(selected) >= top_k:
                break

        return selected

    def search(
        self,
        namespace: str,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Executa recuperação híbrida BM25 + TF-IDF.
        """
        query = (query or "").strip()

        if not query or top_k <= 0:
            return []

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        self._ensure_index(namespace)

        entry = self._cache.get(namespace, {})

        rows = entry.get("rows", [])
        bm25 = entry.get("bm25")

        if not rows or bm25 is None:
            return []

        # ---------------------------------------
        # 1. Recuperação inicial com BM25
        # ---------------------------------------

        raw_bm25_scores = bm25.get_scores(
            query_tokens
        )

        candidate_count = min(
            len(rows),
            max(
                top_k * self.candidate_multiplier,
                top_k,
            ),
        )

        indexes = sorted(
            range(len(raw_bm25_scores)),
            key=lambda index: raw_bm25_scores[index],
            reverse=True,
        )[:candidate_count]

        candidates = [
            rows[index]
            for index in indexes
        ]

        candidate_bm25_scores = [
            raw_bm25_scores[index]
            for index in indexes
        ]

        texts = [
            candidate.get("text", "")
            for candidate in candidates
        ]

        # ---------------------------------------
        # 2. TF-IDF por palavras + caracteres
        # ---------------------------------------

        try:
            word_vectorizer = TfidfVectorizer(
                tokenizer=self._tokenize,
                token_pattern=None,
                lowercase=False,
                ngram_range=(1, 2),
                min_df=1,
            )

            word_matrix = word_vectorizer.fit_transform(
                texts + [query]
            )

            word_document_matrix = word_matrix[:-1]
            word_query_vector = word_matrix[-1]

            word_scores = cosine_similarity(
                word_query_vector,
                word_document_matrix,
            )[0]

            char_vectorizer = TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(3, 5),
                min_df=1,
            )

            char_matrix = char_vectorizer.fit_transform(
                texts + [query]
            )

            char_document_matrix = char_matrix[:-1]
            char_query_vector = char_matrix[-1]

            char_scores = cosine_similarity(
                char_query_vector,
                char_document_matrix,
            )[0]

        except ValueError:
            return []

        # 70% palavras/stemming
        # 30% similaridade morfológica por caracteres
        tfidf_scores = (
            0.70 * word_scores
            + 0.30 * char_scores
        )

        # ---------------------------------------
        # 3. Normalização do BM25
        # ---------------------------------------

        normalized_bm25_scores = _normalize_scores(
            candidate_bm25_scores
        )

        # ---------------------------------------
        # 4. Ranking híbrido
        # ---------------------------------------

        ranked_results = []

        for position, candidate in enumerate(candidates):
            bm25_score = normalized_bm25_scores[position]
            tfidf_score = float(
                tfidf_scores[position]
            )

            final_score = (
                self.bm25_weight * bm25_score
                + self.tfidf_weight * tfidf_score
            )

            ranked_results.append(
                {
                    "id": candidate["id"],
                    "document": candidate.get(
                        "text",
                        "",
                    ),
                    "metadata": candidate.get(
                        "meta",
                        {},
                    ),
                    "score": float(final_score),
                    "bm25_score": float(bm25_score),
                    "tfidf_score": tfidf_score,
                }
            )

        # ---------------------------------------
        # 5. Ordenação final
        # ---------------------------------------

        ranked_results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        # ---------------------------------------
        # 6. Deduplicação
        # ---------------------------------------

        return self._remove_duplicates(
            ranked_results,
            top_k=top_k,
        )