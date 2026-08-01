from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag.retriever import retrieve_documents


app = FastAPI(
    title="RAG Retrieval Service"
)


class RetrievalRequest(BaseModel):
    question: str
    top_k: int = 6


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "rag-service",
    }


@app.post("/retrieve")
def retrieve(request: RetrievalRequest):
    try:
        chunks = retrieve_documents(
            question=request.question,
            top_k=request.top_k,
        )

        return {
            "question": request.question,
            "count": len(chunks),
            "chunks": chunks,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )