from app.rag.pinecone_client import PineconeClient


class ProjectRetriever:
    def __init__(self, client: PineconeClient) -> None:
        self.client = client

    def retrieve(self, project_id: str, query: str, top_k: int = 5) -> list[dict]:
        return self.client.query(project_id, query, top_k=top_k)
