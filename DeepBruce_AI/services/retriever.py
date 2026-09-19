import re
from dataclasses import dataclass, field
from typing import Any, Dict, List


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?。！？])\s+|\n+")
_WHITESPACE = re.compile(r"[ \t]+")


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    position: int
    source: str = ""
    title: str = ""
    url: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> Dict[str, Any]:
        meta = {
            "position": self.position,
            "source": self.source,
            "title": self.title,
            "url": self.url,
            **self.metadata,
        }

        return {
            "id": self.id,
            "text": self.text,
            "meta": meta,
        }


def split_sentences(text: str) -> List[str]:
    """
    Divide texto em frases preservando unidades úteis para chunking
    e para o TextRank legado de qa.py.
    """
    text = (text or "").strip()

    if not text:
        return []

    parts = []

    for piece in _SENTENCE_SPLIT.split(text):
        normalized = _WHITESPACE.sub(" ", piece).strip()

        if normalized:
            parts.append(normalized)

    return parts


def _split_oversized_text(text: str, max_chars: int) -> List[str]:
    """
    Divide uma unidade maior que max_chars tentando preservar palavras.
    """
    if len(text) <= max_chars:
        return [text]

    words = text.split()

    if not words:
        return []

    parts = []
    current = []

    for word in words:
        candidate = " ".join(current + [word])

        if current and len(candidate) > max_chars:
            parts.append(" ".join(current))
            current = []

        if len(word) > max_chars:
            if current:
                parts.append(" ".join(current))
                current = []

            for start in range(0, len(word), max_chars):
                parts.append(word[start:start + max_chars])

            continue

        current.append(word)

    if current:
        parts.append(" ".join(current))

    return parts


def _prepare_units(text: str, max_chars: int) -> List[str]:
    units = []

    for sentence in split_sentences(text):
        units.extend(
            _split_oversized_text(
                sentence,
                max_chars=max_chars,
            )
        )

    return units


def build_chunks(
    text: str,
    *,
    source_id: str,
    source: str = "",
    title: str = "",
    url: str = "",
    max_chars: int = 1400,
    overlap_sentences: int = 2,
    metadata: Dict[str, Any] | None = None,
) -> List[Chunk]:
    """
    Constrói chunks com tamanho controlado, overlap e metadados.

    O overlap reaproveita as últimas unidades do chunk anterior,
    reduzindo perda de contexto nas fronteiras entre chunks.
    """
    if max_chars <= 0:
        raise ValueError("max_chars deve ser maior que zero.")

    if overlap_sentences < 0:
        raise ValueError("overlap_sentences não pode ser negativo.")

    source_id = (source_id or "").strip()

    if not source_id:
        raise ValueError("source_id é obrigatório.")

    units = _prepare_units(text, max_chars)

    if not units:
        return []

    chunks: List[Chunk] = []
    current: List[str] = []

    def append_chunk(parts: List[str]) -> None:
        chunk_text = " ".join(parts).strip()

        if not chunk_text:
            return

        position = len(chunks)

        chunks.append(
            Chunk(
                id=f"{source_id}-{position:04d}",
                text=chunk_text,
                position=position,
                source=source,
                title=title,
                url=url,
                metadata=dict(metadata or {}),
            )
        )

    for unit in units:
        candidate = " ".join(current + [unit])

        if current and len(candidate) > max_chars:
            append_chunk(current)

            overlap_count = min(
                overlap_sentences,
                len(current),
            )

            current = (
                current[-overlap_count:]
                if overlap_count
                else []
            )

            while (
                current
                and len(" ".join(current + [unit])) > max_chars
            ):
                current.pop(0)

        current.append(unit)

    if current:
        final_text = " ".join(current).strip()

        if not chunks or chunks[-1].text != final_text:
            append_chunk(current)

    return chunks