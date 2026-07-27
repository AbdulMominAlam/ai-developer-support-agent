# AI Developer Support Agent

An AI-powered Developer Support Agent built using the OpenAI Responses API, Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP), FastAPI, PostgreSQL, and React.

The application assists developers by answering documentation questions, retrieving customer account information, creating support tickets, and interacting with GitHub repositories through MCP tools. It supports persistent multi-turn conversations using PostgreSQL-backed session memory and provides a web-based chat interface for demonstration.

---

## Features

- Multi-turn AI conversations using the OpenAI Responses API
- Retrieval-Augmented Generation (RAG) using ChromaDB
- Documentation question answering using Supabase documentation
- MCP integration with custom developer support tools
- GitHub MCP integration for repository, issue, and file operations
- PostgreSQL (Neon) database for persistent account, ticket, and session storage
- Session-based conversation memory
- Bearer Token Authentication
- FastAPI REST API
- React frontend for interacting with the AI agent
- API testing with Postman

---

## Tech Stack

### Frontend

- React
- Vite
- Axios

### Backend

- Python
- FastAPI
- OpenAI Responses API
- PostgreSQL (Neon)
- Psycopg
- MCP Python SDK

### AI

- GPT (OpenAI Responses API)
- Retrieval-Augmented Generation (RAG)
- ChromaDB
- LangChain
- Embeddings

### MCP Servers

- Custom Developer Support MCP Server
- GitHub Official MCP Server

---

# Project Architecture

```
                React Frontend
                       │
                       ▼
                FastAPI Backend
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
 OpenAI Responses API         MCP Tool Calls
         │                           │
         ▼                           ▼
      GPT Model                PostgreSQL
                               ChromaDB
                               GitHub MCP
```

---

## Project Structure

```
developer-support-agent/

├── frontend/                 # React frontend
│
├── rag/
│   ├── ingest.py
│   ├── retriever.py
│   └── answer.py
│
├── clients/
│   ├── mcp_client.py
│   └── github_mcp_client.py
│
├── mcp_servers/
│   └── developer_support_server.py
│
├── api.py
├── agent.py
├── tools.py
├── database.py
├── sessions.py
├── import_data.py
├── setup_database.py
├── config.py
└── main.py
```

---

# How It Works

The application begins in the React frontend, where the user enters a query through the chat interface. The frontend sends the user's message and session ID to the FastAPI `/chat` endpoint using Axios.

FastAPI first authenticates the request using a Bearer Token. It then retrieves the latest OpenAI `response_id` associated with the provided session from PostgreSQL before passing the user's message and previous response ID to `process_message()` in `agent.py`.

`process_message()` sends the user's prompt, system instructions, conversation history, and available tools to the OpenAI Responses API. GPT first determines whether it can answer directly or whether one or more tools are required.

If documentation is needed, GPT calls the `search_documentation` tool. The request is routed through `rag/answer.py`, which retrieves relevant document chunks from ChromaDB using LangChain before generating an answer grounded in the retrieved documentation.

If account or ticket information is required, GPT calls the custom Developer Support MCP Server. The MCP server executes SQL queries against PostgreSQL to retrieve account information or create new support tickets.

If GitHub information is required, GPT calls one of the GitHub MCP tools, which communicate with GitHub's official MCP Server to retrieve repositories, issues, or file contents.

After the required tools return their results, `agent.py` sends those results back to the OpenAI Responses API in a second request. GPT combines the retrieved information with the user's original request to generate a final natural-language response.

The API then stores the newest OpenAI `response_id` in PostgreSQL, allowing future requests within the same session to continue the conversation with full context. Finally, the completed response is returned to the React frontend and displayed to the user.

---

# Session-Based Conversation Memory

Conversation memory is managed entirely by the backend using PostgreSQL.

Each conversation is assigned a unique session ID. The backend stores the latest OpenAI response ID associated with that session in a dedicated `sessions` table. For every new request, FastAPI retrieves the stored response ID and passes it to the OpenAI Responses API, allowing GPT to continue the existing conversation without requiring the frontend to manage conversation history.

Selecting **New Chat** creates a brand-new session ID, resulting in a completely independent conversation with no previous context.

---

# PostgreSQL Integration

The application uses PostgreSQL (Neon) instead of JSON files for persistent data storage.

Three database tables are used:

- `accounts`
- `tickets`
- `sessions`

Account lookups, support ticket creation, and conversation session management are all performed using SQL queries, providing a scalable and production-oriented backend.

---

# Authentication

All API endpoints are protected using Bearer Token Authentication.

Every request must include:

```
Authorization: Bearer <API_TOKEN>
```

FastAPI validates the token before processing any request.

---

# Running the Project

## Backend

```bash
pip install -r requirements.txt

uvicorn api:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Example Prompts

### Account Lookup

```
Who is account ACC-1001?
```

### Follow-up Conversation

```
How many API calls does that account have remaining?
```

### Documentation

```
How do users reset their password?
```

### Support Ticket

```
Create a support ticket for ACC-1001 because the API is returning 500 errors.
```

### GitHub

```
List the open issues in the repository.
```

---

# Future Improvements

- Streaming responses from the OpenAI Responses API
- User authentication and login system
- Conversation history management
- Docker deployment
- Cloud deployment
- Additional MCP server integrations
- Improved UI/UX
- Analytics dashboard

---

# Author

Abdul Momin Alam

Built as part of an AI Engineering Internship project focused on Agentic AI, Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP), OpenAI Responses API, FastAPI, PostgreSQL, and React.