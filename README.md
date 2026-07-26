# AI Developer Support Agent

An AI-powered developer support assistant built with the **OpenAI Responses API**, **Retrieval-Augmented Generation (RAG)**, **ChromaDB**, **PostgreSQL (Neon)**, **FastAPI**, and the **Model Context Protocol (MCP)**.

The agent can answer technical questions from Supabase documentation, retrieve developer account information, create support tickets, maintain context across multi-turn conversations, and expose all functionality through both an interactive CLI and a REST API.

---

# Features

- Answers Supabase documentation questions using RAG
- Retrieves relevant document chunks from ChromaDB
- Includes source citations in documentation answers
- Uses an LLM to automatically select the correct tool
- Looks up developer accounts through a custom MCP server
- Creates and stores support tickets in PostgreSQL
- Supports multi-turn conversation memory using `previous_response_id`
- Bearer Token Authentication for secure API access
- Understands follow-up references such as:
  - "it"
  - "that account"
  - "the same user"
- Provides natural-language responses instead of raw JSON
- Includes an interactive terminal chat interface
- Exposes the agent through a FastAPI REST API
- Supports testing with Postman
- Automatically generates OpenAPI / Swagger documentation

---

# Example Conversation

```text
You: Show me account ACC-1001

Agent:
Account ACC-1001 belongs to Aisha Khan.
The account is active on the Pro plan and has used
8,200 of its 10,000 monthly API calls.

You: How many API calls does it have left?

Agent:
It has 1,800 monthly API calls remaining.

You: Create a support ticket for it because the database is failing.

Agent:
Support ticket TKT-0027 was created successfully
for account ACC-1001.

You: What was the ticket ID?

Agent:
The ticket ID is TKT-0027.
```

---

# Architecture

```text
                    User / Postman
                          |
                          v
              Bearer Token Authentication
                          |
                          v
                   FastAPI (api.py)
                          |
                          v
                  process_message()
                          |
                          v
               OpenAI Responses API
            Intent and Tool Selection
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
   Direct Reply      RAG Pipeline      MCP Client
                          |                 |
                          v                 v
                      ChromaDB     Developer Support MCP
                          |                 |
                          v          +------+------+
                   Supabase Docs     |             |
                                     v             v
                              Account Lookup   Ticket Creation
                                     |             |
                                     +------+------+
                                            |
                                            v
                                   PostgreSQL (Neon)
```

---

# How It Works

## 1. User Request

A user sends a message either:

- through the terminal (`main.py`), or
- through the FastAPI `/chat` endpoint.

---

## 2. Authentication

Every request to the API must include a valid Bearer Token.

If authentication succeeds, the request is processed.
Otherwise, the API returns:

```text
401 Unauthorized
```

---

## 3. Intent Detection

The request is forwarded to the OpenAI Responses API.

The model decides whether to:

- answer directly
- search documentation
- retrieve an account
- create a support ticket

---

## 4. RAG

For documentation questions:

1. Documents are split into chunks.
2. Chunks are converted into embeddings.
3. Embeddings are stored in ChromaDB.
4. The user's question is embedded.
5. Similar chunks are retrieved.
6. Retrieved context is sent to the LLM.
7. The final grounded answer is generated.

---

## 5. MCP

Developer actions are handled through a custom MCP server.

```text
Agent
  |
  v
MCP Client
  |
  v
Developer Support MCP Server
  |
  +-- get_account
  |
  +-- create_support_ticket
```

---

## 6. PostgreSQL

Developer accounts and support tickets are stored in a PostgreSQL database hosted on Neon.

The MCP tools execute SQL queries to retrieve and update data instead of reading local JSON files.

---

## 7. Conversation Memory

The Responses API uses `previous_response_id` to continue conversations without resending the full history.

---

# REST API

Start the API server:

```bash
uvicorn api:app --reload
```

Default address:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

## Authentication

Include the Bearer Token in every request.

```
Authorization: Bearer YOUR_API_TOKEN
```

---

## POST /chat

Request

```json
{
  "message": "How do I reset my Supabase password?",
  "previous_response_id": null
}
```

Response

```json
{
  "type": "rag",
  "answer": "...",
  "tool": "search_documentation",
  "response_id": "resp_..."
}
```

---

# Remote Testing

The API can be exposed securely using ngrok.

```bash
ngrok http 8000
```

This creates a temporary public HTTPS URL that forwards requests to the local FastAPI server.

---

# Technologies

- Python
- FastAPI
- OpenAI Responses API
- OpenAI Embeddings
- Retrieval-Augmented Generation (RAG)
- ChromaDB
- PostgreSQL
- Neon
- Model Context Protocol (MCP)
- AsyncIO
- Postman
- ngrok

---

# Project Structure

```text
ai-developer-support-agent/
|
|-- api.py
|-- agent.py
|-- main.py
|-- tools.py
|-- database.py
|-- setup_database.py
|-- import_data.py
|-- config.py
|-- requirements.txt
|-- README.md
|
|-- clients/
|   |-- mcp_client.py
|
|-- mcp_servers/
|   |-- developer_support_server.py
|
|-- rag/
|   |-- ingest.py
|   |-- retriever.py
|   |-- answer.py
|
|-- data/
|   |-- accounts.json
|   |-- tickets.json
|
|-- chroma_db/
|
|-- documents/
|
|-- examples/
|
|-- memory/
|
|-- test_agent.py
|-- test_tools.py
```

---

# Setup

```bash
git clone https://github.com/AbdulMominAlam/ai-developer-support-agent.git

cd ai-developer-support-agent

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=your_model_name
DATABASE_URL=your_neon_database_url
API_TOKEN=your_api_token
```

---

# Build the Vector Database

Place documentation inside:

```text
documents/
```

Then run:

```bash
python rag/ingest.py
```

---

# Run

CLI

```bash
python main.py
```

API

```bash
uvicorn api:app --reload
```

---

# Available Tools

- `search_documentation`
- `get_account`
- `create_support_ticket`

---

# Example Tool Routing

| User Request | Selected Path |
|--------------|---------------|
| How do I reset a password? | RAG |
| Show me account ACC-1001 | MCP |
| Create a support ticket | MCP |
| Hello | Direct Response |
| How much usage does it have left? | Conversation Memory |

---

# Security

- Bearer Token Authentication
- API keys stored in `.env`
- PostgreSQL credentials stored in `.env`
- `.env` excluded by `.gitignore`
- Parameterized SQL queries
- No secrets committed to Git

---

# Future Improvements

- Session-based conversation management
- Automatic session expiration
- GitHub MCP integration
- React frontend
- Streaming responses
- User authentication
- Better logging
- More automated tests

---

# License

MIT License

---

# Author

**Abdul Momin Alam**

GitHub: https://github.com/AbdulMominAlam