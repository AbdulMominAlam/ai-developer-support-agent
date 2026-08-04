# AI Developer Support Agent

Production-inspired AI Developer Support Platform built with the OpenAI Responses API, RAG, MCP, FastAPI, RabbitMQ, WebSockets, PostgreSQL, and React.

## Overview

The AI Developer Support Agent is an end-to-end support platform that combines large language models with modern backend architecture. The application answers documentation questions using Retrieval-Augmented Generation (RAG), retrieves developer account information, creates support tickets, and interacts with GitHub repositories through the Model Context Protocol (MCP).

Unlike a traditional chatbot, the project separates responsibilities across multiple services. Documentation retrieval is handled by a dedicated RAG microservice, support ticket creation is processed asynchronously using RabbitMQ, and AI responses are streamed to the frontend in real time using WebSockets.

## Features

- Multi-turn conversations using the OpenAI Responses API
- Real-time streaming responses using WebSockets
- Retrieval-Augmented Generation (RAG)
  - Dedicated FastAPI RAG microservice
  - ChromaDB vector database
  - OpenAI Embeddings
- Custom Developer Support MCP Server
- GitHub Official MCP Server integration
- RabbitMQ-based asynchronous support ticket processing
- Background support worker
- PostgreSQL (Neon) for accounts, tickets, and session memory
- Session-based conversation memory
- Bearer token authentication
- React + Vite frontend
- REST API testing with Postman

## Tech Stack

**Frontend**
- React
- Vite
- Axios

**Backend**
- Python
- FastAPI
- WebSockets
- RabbitMQ
- HTTPX
- PostgreSQL (Neon)
- Psycopg

**AI**
- OpenAI Responses API
- GPT
- Retrieval-Augmented Generation (RAG)
- ChromaDB
- LangChain
- OpenAI Embeddings

**Tool Integration**
- Model Context Protocol (MCP)
- Custom Developer Support MCP Server
- GitHub Official MCP Server

## System Architecture

                   React Frontend
                           │
                  WebSocket / HTTP
                           │
                    FastAPI Agent
        ┌────────────┼─────────────┐
        │            │             │
        ▼            ▼             ▼
   RAG Service    RabbitMQ     GitHub MCP
      │              │
      ▼              ▼
   ChromaDB    Support Worker
                     │
                     ▼
          Developer Support MCP
                     │
                     ▼
              PostgreSQL (Neon)


## Key Design Decisions

| Technology | Why it was used |
|---|---|
| WebSockets | Stream AI responses to the frontend in real time instead of waiting for the complete response. |
| HTTP | Communication between the Agent and RAG service, since documentation retrieval is needed immediately before GPT can answer. |
| RabbitMQ | Queue background support-ticket creation so the chatbot remains responsive under load. |
| MCP | Standard interface for custom developer tools and GitHub tools. |
| PostgreSQL | Persistent storage for accounts, tickets, and conversation sessions. |

## How It Works

### 1. User Request
The user sends a message from the React frontend. The frontend communicates with the FastAPI backend through HTTP and WebSockets — WebSockets stream AI responses token-by-token, while HTTP is used for standard API communication.

### 2. Agent
The FastAPI backend forwards the request to the OpenAI Responses API together with:
- System prompt
- Previous conversation (`response_id`)
- Available tools

GPT decides whether a tool is required.

### 3. Documentation Questions
If documentation is needed:
1. The Agent sends an HTTP request to the dedicated RAG microservice.
2. The RAG service generates an embedding for the user's question.
3. ChromaDB retrieves the most relevant document chunks.
4. Those chunks are returned to the Agent.
5. GPT generates an answer grounded only in the retrieved documentation.

The RAG logic is isolated inside its own service, allowing it to be developed, deployed, and scaled independently.

### 4. Support Ticket Creation
If the user requests a support ticket:
1. The Agent publishes a message to RabbitMQ.
2. RabbitMQ stores the request in a durable queue.
3. A background worker consumes the message.
4. The worker calls the Developer Support MCP Server.
5. The MCP Server creates the support ticket in PostgreSQL.

Using RabbitMQ allows ticket creation to happen asynchronously without blocking the chatbot.

### 5. Account Lookup
Account lookups are performed through the custom Developer Support MCP Server. Since the Agent requires the result immediately, this communication remains synchronous instead of using RabbitMQ.

### 6. GitHub Operations
Repository search, issue retrieval, and file reading are handled through GitHub's Official MCP Server.

### 7. Conversation Memory
Conversation memory is stored in PostgreSQL. Each session stores the latest OpenAI `response_id`, allowing the OpenAI Responses API to continue conversations without the frontend managing message history.

## Microservice Architecture

The application follows a hybrid microservice architecture:

- **Agent Service** — Coordinates the conversation and tool execution.
- **RAG Service** — Dedicated FastAPI microservice responsible for document retrieval.
- **Support Worker** — Background worker responsible for processing RabbitMQ ticket requests.
- **Developer Support MCP Server** — Provides account lookup and ticket creation tools.
- **GitHub MCP Server** — Provides GitHub repository tools.

Each service has a single responsibility and communicates using the most appropriate mechanism:

| Mechanism | Purpose |
|---|---|
| HTTP | Synchronous request/response |
| RabbitMQ | Asynchronous background processing |
| MCP | Standardized tool execution |
| WebSockets | Real-time frontend streaming |

## Project Structure

\`\`\`
developer-support-agent/
├── frontend/
├── rag/
│   ├── ingest.py
│   ├── retriever.py
│   └── answer.py
├── rag_service/
│   └── main.py
├── support_service/
│   ├── producer.py
│   └── worker.py
├── clients/
│   ├── rag_client.py
│   ├── mcp_client.py
│   └── github_mcp_client.py
├── mcp_servers/
├── api.py
├── agent.py
├── database.py
├── sessions.py
├── tools.py
└── config.py
\`\`\`

## Running the Project

**Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Start the Agent API**
\`\`\`bash
uvicorn api:app --reload
\`\`\`

**Start the RAG Service**
\`\`\`bash
uvicorn rag_service.main:app --port 8002 --reload
\`\`\`

**Start the RabbitMQ Worker**
\`\`\`bash
python -m support_service.worker
\`\`\`

**Start the Frontend**
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

## Example Prompts

**Documentation**
> How do users reset their password?

**Account Lookup**
> Who is account ACC-1001?

**Support Ticket**
> Create a support ticket for ACC-1001 because password reset emails are not arriving.

**GitHub**
> List the open issues for the repository.

## Future Improvements

- [ ] Dockerize each microservice
- [ ] Kubernetes deployment
- [ ] Redis caching
- [ ] Multiple RabbitMQ workers
- [ ] Request-reply RabbitMQ messaging
- [ ] Additional MCP server integrations
- [ ] CI/CD with GitHub Actions
- [ ] Prometheus & Grafana monitoring
- [ ] Cloud deployment

## Author

**Abdul Momin Alam**

Built as part of an AI Engineering Internship focused on Agentic AI, Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP), OpenAI Responses API, FastAPI, RabbitMQ, WebSockets, PostgreSQL, and React.