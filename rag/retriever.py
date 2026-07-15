from pathlib import Path
import sys

import chromadb
from openai import OpenAI


# Add the main project folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
)


def retrieve_documents(question, top_k=6):
    """
    Find the document chunks that are most relevant
    to the user's question.
    """

    # Create the OpenAI client
    openai_client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    # Convert the user's question into an embedding
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=question,
    )

    # OpenAI returns a list of embedding results.
    # Since we only send one question, take the first and only embedding.
    question_embedding = response.data[0].embedding

    # Connect to the existing Chroma database
    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # Open the collection created during ingestion
    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )

    # Search for the most similar chunks
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    retrieved_chunks = []

    # Chroma returns a list of results for each query.
    # We only searched one question, so take the first query's results.
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for index in range(len(documents)):
        document_text = documents[index]
        metadata = metadatas[index]
        distance = distances[index]

        retrieved_chunk = {
            "text": document_text,
            "source": metadata["source"],
            "chunk_number": metadata["chunk_number"],
            "distance": distance,
        }

        retrieved_chunks.append(retrieved_chunk)

    return retrieved_chunks


def main():
    question = input(
        "Ask a Supabase documentation question: "
    )

    # The standalone retriever test returns 4 chunks by default.
    results = retrieve_documents(question)

    print("\n--- Retrieved Chunks ---\n")

    result_number = 1

    for result in results:
        print(f"Result {result_number}")
        print(f"Source: {result['source']}")
        print(f"Chunk: {result['chunk_number']}")
        print(f"Distance: {result['distance']:.4f}")
        print()
        print(result["text"])
        print("\n" + "-" * 70 + "\n")

        result_number = result_number + 1


# Only run main() when this file is executed directly.
# Do not run main() when another file imports retrieve_documents().
if __name__ == "__main__":
    main()