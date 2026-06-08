class PineconeClient:
    """Placeholder for project-scoped Pinecone operations added in v0.3."""

    def upsert_documents(self, project_id: str, documents: list[dict]) -> None:
        raise NotImplementedError("Pinecone indexing is planned for v0.3.")

    def query(self, project_id: str, query: str, top_k: int = 5) -> list[dict]:
        raise NotImplementedError("Pinecone retrieval is planned for v0.3.")
