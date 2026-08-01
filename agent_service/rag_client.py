import httpx


RAG_SERVICE_URL = "http://localhost:8002"


async def retrieve_documents_from_service(
    question: str,
    top_k: int = 6,
) -> list[dict]:
    async with httpx.AsyncClient() as client:       
        response = await client.post(
            f"{RAG_SERVICE_URL}/retrieve",
            json={
                "question": question,
                "top_k": top_k,
            },
            timeout=30.0,
        )

        response.raise_for_status()

        data = response.json()

        return data["chunks"]       