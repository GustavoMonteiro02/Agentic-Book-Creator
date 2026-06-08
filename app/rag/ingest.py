from __future__ import annotations

from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class SourceChunk:
    text: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)


def chunk_source_text(text: str, chunk_size: int = 1200) -> list[str]:
    return [chunk.text for chunk in chunk_by_tokens(text, chunk_size=chunk_size)]


def chunk_by_tokens(text: str, chunk_size: int = 1200, overlap: int = 0, metadata: dict | None = None) -> list[SourceChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    chunks = []
    step = chunk_size - overlap

    index = 0
    start = 0
    while start < len(words):
        chunk_words = words[start : start + chunk_size]
        if not chunk_words:
            break
        chunks.append(
            SourceChunk(
                text=" ".join(chunk_words),
                chunk_index=index,
                metadata={
                    **(metadata or {}),
                    "chunking_strategy": (metadata or {}).get("chunking_strategy", "fixed_size"),
                    "chunk_size": chunk_size,
                    "overlap": overlap,
                },
            )
        )
        if start + chunk_size >= len(words):
            break
        index += 1
        start += step
    return chunks


def chunk_by_headings(text: str, max_words: int = 1200, overlap: int = 80, metadata: dict | None = None) -> list[SourceChunk]:
    effective_overlap = min(overlap, max_words - 1) if max_words > 1 else 0
    sections = split_markdown_sections(text)
    chunks: list[SourceChunk] = []

    for section in sections:
        section_metadata = {
            **(metadata or {}),
            "chunking_strategy": "heading_aware",
            "heading": section["heading"],
            "heading_level": section["level"],
        }
        section_chunks = chunk_by_tokens(section["text"], chunk_size=max_words, overlap=effective_overlap, metadata=section_metadata)
        for chunk in section_chunks:
            chunks.append(SourceChunk(text=chunk.text, chunk_index=len(chunks), metadata=chunk.metadata))

    return chunks


def split_markdown_sections(text: str) -> list[dict]:
    lines = text.splitlines()
    sections: list[dict] = []
    current_heading = "Document"
    current_level = 0
    current_lines: list[str] = []

    for line in lines:
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if heading_match:
            _append_section(sections, current_heading, current_level, current_lines)
            current_heading = heading_match.group(2).strip()
            current_level = len(heading_match.group(1))
            current_lines = [line]
        else:
            current_lines.append(line)

    _append_section(sections, current_heading, current_level, current_lines)
    return sections or [{"heading": "Document", "level": 0, "text": text.strip()}]


def _append_section(sections: list[dict], heading: str, level: int, lines: list[str]) -> None:
    section_text = "\n".join(lines).strip()
    if section_text:
        sections.append({"heading": heading, "level": level, "text": section_text})
