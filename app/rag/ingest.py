def chunk_source_text(text: str, chunk_size: int = 1200) -> list[str]:
    words = text.split()
    chunks = []
    for index in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[index : index + chunk_size]))
    return chunks
