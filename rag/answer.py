from pathlib import Path
import sys
import asyncio

from openai import OpenAI


# Add the main project folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from config import MODEL_NAME, OPENAI_API_KEY
from agent_service.rag_client import retrieve_documents_from_service


def build_context(retrieved_chunks):
    """
    Combine the retrieved chunks into one context string.
    """

    context = ""

    for chunk in retrieved_chunks:
        context = context + f"""
Source: {chunk["source"]}

{chunk["text"]}

------------------------------
"""

    return context


async def answer_question(question):
    """
    Retrieve relevant chunks and ask GPT to answer
    using only those chunks.
    """

    retrieved_chunks = await retrieve_documents_from_service(
        question=question,
        top_k=6,
    )

    context = build_context(retrieved_chunks)

    prompt = f"""
You are a Supabase documentation support assistant.

Answer the user's question using ONLY the retrieved documentation below.

Rules:
- Do not use outside knowledge.
- Do not invent information.
- Keep the answer clear and concise.
- Combine information from multiple retrieved chunks when necessary.
- If information is spread across different chunks, summarize it together.
- If the answer is not present in the documentation, say exactly:
  "I could not find that information in the available documentation."
- If the answer is not found, write:
  "Sources: None"
- Otherwise, include a Sources section at the end.
- Include only filenames that directly support the answer.
- Do not cite unrelated retrieved documents.
- Do not mention chunk numbers.

Retrieved documentation:

{context}

User question:

{question}
"""

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
    )

    return response.output_text


async def main():
    question = input(
        "Ask a Supabase documentation question: "
    )

    answer = await answer_question(question)

    print("\n--- Answer ---\n")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())