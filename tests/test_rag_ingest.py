from app.rag.ingest import chunk_by_headings, chunk_by_tokens, chunk_source_text, split_markdown_sections


def test_chunk_by_tokens_supports_overlap_and_metadata():
    text = "one two three four five six"

    chunks = chunk_by_tokens(text, chunk_size=3, overlap=1, metadata={"source_id": "doc-1"})

    assert [chunk.text for chunk in chunks] == ["one two three", "three four five", "five six"]
    assert chunks[0].metadata["source_id"] == "doc-1"
    assert chunks[0].metadata["chunking_strategy"] == "fixed_size"


def test_split_markdown_sections_preserves_headings():
    text = """# Intro
Opening text.

## Details
Technical text.
"""

    sections = split_markdown_sections(text)

    assert sections[0]["heading"] == "Intro"
    assert sections[0]["level"] == 1
    assert sections[1]["heading"] == "Details"
    assert sections[1]["level"] == 2


def test_chunk_by_headings_attaches_heading_metadata():
    text = """# RAG
Retrieval augmented generation uses embeddings.

# Evaluation
Measure recall and precision.
"""

    chunks = chunk_by_headings(text, max_words=20)

    assert len(chunks) == 2
    assert chunks[0].metadata["chunking_strategy"] == "heading_aware"
    assert chunks[0].metadata["heading"] == "RAG"
    assert chunks[1].metadata["heading"] == "Evaluation"


def test_legacy_chunk_source_text_returns_strings():
    chunks = chunk_source_text("one two three four", chunk_size=2)

    assert chunks == ["one two", "three four"]
