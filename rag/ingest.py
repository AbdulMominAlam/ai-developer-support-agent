from pathlib import Path
import sys

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI


# Add the main project folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    DOCUMENTS_DIR,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
)


def load_documents():
    """
    Load all .mdx files from the documents folder.
    """

    documents = []

    files = sorted(DOCUMENTS_DIR.glob("*.mdx"))

    for file_path in files:
        text = file_path.read_text(encoding="utf-8")

        document = {
            "text": text,
            "source": file_path.name,
        }

        documents.append(document)

    if len(documents) == 0:
        raise FileNotFoundError(
            f"No .mdx files found inside {DOCUMENTS_DIR}"
        )

    return documents


def create_chunks(documents):
    """
    Split every document into smaller overlapping chunks.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    all_chunks = []

    for document in documents:
        document_text = document["text"]
        document_source = document["source"]

        split_texts = text_splitter.split_text(document_text)

        for chunk_number, chunk_text in enumerate(split_texts):
            chunk = {
                "text": chunk_text,
                "source": document_source,
                "chunk_number": chunk_number,
            }

            all_chunks.append(chunk)

    return all_chunks


def create_embeddings(client, chunks):
    """
    Convert every chunk into an embedding vector.
    """

    chunk_texts = []

    for chunk in chunks:
        chunk_texts.append(chunk["text"])

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=chunk_texts,
    )

    embeddings = []

    for item in response.data:
        embeddings.append(item.embedding)

    return embeddings


def store_in_chroma(chunks, embeddings):
    """
    Store the chunks, embeddings, and metadata in ChromaDB.
    """

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # Delete the old collection if it already exists
    try:
        chroma_client.delete_collection(
            name=COLLECTION_NAME
        )
    except Exception:
        pass

    # Create a fresh collection
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME
    )

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        chunk_id = (
            chunk["source"]
            + "-chunk-"
            + str(chunk["chunk_number"])
        )

        metadata = {
            "source": chunk["source"],
            "chunk_number": chunk["chunk_number"],
        }

        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append(metadata)

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def main():
    print("Loading Supabase documentation...")

    documents = load_documents()

    print(f"Loaded {len(documents)} documents.")

    print("Splitting documents into chunks...")

    chunks = create_chunks(documents)

    print(f"Created {len(chunks)} chunks.")

    print("Creating OpenAI embeddings...")

    openai_client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    embeddings = create_embeddings(
        openai_client,
        chunks,
    )

    print(f"Created {len(embeddings)} embeddings.")

    print("Saving chunks to ChromaDB...")

    store_in_chroma(
        chunks,
        embeddings,
    )

    print(
        f"Finished. Stored {len(chunks)} chunks "
        f"in collection '{COLLECTION_NAME}'."
    )


if __name__ == "__main__":
    main()