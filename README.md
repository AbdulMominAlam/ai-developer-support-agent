AI Developer Support Agent

Production-inspired AI Developer Support Platform built with theOpenAI Responses API, RAG, MCP, FastAPI, RabbitMQ,WebSockets, PostgreSQL, and React.

Overview

The AI Developer Support Agent is an end-to-end support platform thatcombines large language models with modern backend architecture. Theapplication answers documentation questions using Retrieval-AugmentedGeneration (RAG), retrieves developer account information, createssupport tickets, and interacts with GitHub repositories through theModel Context Protocol (MCP).

Unlike a traditional chatbot, the project separates responsibilitiesacross multiple services. Documentation retrieval is handled by adedicated RAG microservice, support ticket creation is processedasynchronously using RabbitMQ, and AI responses are streamed to thefrontend in real time using WebSockets.

Features

Multi-turn conversations using the OpenAI Responses API

Real-time streaming responses using WebSockets

Retrieval-Augmented Generation (RAG)

Dedicated FastAPI RAG microservice

ChromaDB vector database

OpenAI Embeddings

Custom Developer Support MCP Server

GitHub Official MCP Server integration

RabbitMQ-based asynchronous support ticket processing

Background support worker

PostgreSQL (Neon) for accounts, tickets and session memory

Session-based conversation memory

Bearer Token Authentication

React + Vite frontend

REST API testing with Postman

Tech Stack

Frontend

React

Vite

Axios

Backend

Python

FastAPI

WebSockets

RabbitMQ

HTTPX

PostgreSQL (Neon)

Psycopg

AI

OpenAI Responses API

GPT

Retrieval-Augmented Generation (RAG)

ChromaDB

LangChain

OpenAI Embeddings

Tool Integration

Model Context Protocol (MCP)

Custom Developer Support MCP Server

GitHub Official MCP Server

System Architecture

                    React Frontend
                           │
                  WebSocket / HTTP
                           │
                    FastAPI Agent
        ┌────────────┼─────────────┐
        │            │             │
        ▼            ▼             ▼
   RAG Service   RabbitMQ     GitHub MCP
      HTTP          │
        │           ▼
        ▼      Support Worker
   ChromaDB         │
                    ▼
        Developer Support MCP
                    │
                    ▼
             PostgreSQL (Neon)

Key Design Decisions

Technology                    Why it was used

WebSockets                    Stream AI responses to the frontend inreal time instead of waiting for thecomplete response.

HTTP                          Communication between the Agent and RAGservice because documentation retrievalis needed immediately before GPT cananswer.

RabbitMQ                      Queue background support-ticket creationso the chatbot remains responsive underload.

MCP                           Standard interface for custom developertools and GitHub tools.

PostgreSQL                    Persistent storage for accounts, ticketsand conversation sessions.

How It Works

1. User Request

The user sends a message from the React frontend.

The frontend communicates with the FastAPI backend through HTTP andWebSockets. WebSockets stream AI responses token-by-token while HTTP isused for standard API communication.

2. Agent

The FastAPI backend forwards the request to the OpenAI Responses APItogether with:

System prompt

Previous conversation (response_id)

Available tools

GPT decides whether a tool is required.

3. Documentation Questions

If documentation is needed:

The Agent sends an HTTP request to the dedicated RAG microservice.

The RAG service generates an embedding for the user's question.

ChromaDB retrieves the most relevant document chunks.

Those chunks are returned to the Agent.

GPT generates an answer grounded only in the retrieveddocumentation.

The RAG logic is isolated inside its own service, allowing it to bedeveloped, deployed and scaled independently.

4. Support Ticket Creation

If the user requests a support ticket:

The Agent publishes a message to RabbitMQ.

RabbitMQ stores the request in a durable queue.

A background worker consumes the message.

The worker calls the Developer Support MCP Server.

The MCP Server creates the support ticket in PostgreSQL.

Using RabbitMQ allows ticket creation to happen asynchronously withoutblocking the chatbot.

5. Account Lookup

Account lookups are performed through the custom Developer Support MCPServer.

Since the Agent requires the result immediately, this communicationremains synchronous instead of using RabbitMQ.

6. GitHub Operations

Repository search, issue retrieval and file reading are handled throughGitHub's Official MCP Server.

7. Conversation Memory

Conversation memory is stored in PostgreSQL.

Each session stores the latest OpenAI response_id, allowing the OpenAIResponses API to continue conversations without the frontend managingmessage history.

Microservice Architecture

The application follows a hybrid microservice architecture.

Agent Service -- Coordinates the conversation and toolexecution.

RAG Service -- Dedicated FastAPI microservice responsible fordocument retrieval.

Support Worker -- Background worker responsible for processingRabbitMQ ticket requests.

Developer Support MCP Server -- Provides account lookup andticket creation tools.

GitHub MCP Server -- Provides GitHub repository tools.

Each service has a single responsibility and communicates using the mostappropriate mechanism:

HTTP → synchronous request/response

RabbitMQ → asynchronous background processing

MCP → standardized tool execution

WebSockets → real-time frontend streaming

Project Structure

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

Running the Project

Install

pip install -r requirements.txt

Start the Agent API

uvicorn api:app --reload

Start the RAG Service

uvicorn rag_service.main:app --port 8002 --reload

Start the RabbitMQ Worker

python -m support_service.worker

Start the Frontend

cd frontend
npm install
npm run dev

Example Prompts

Documentation

How do users reset their password?

Account Lookup

Who is account ACC-1001?

Support Ticket

Create a support ticket for ACC-1001 because password reset emails are not arriving.

GitHub

List the open issues for the repository.

Future Improvements

Dockerize each microservice

Kubernetes deployment

Redis caching

Multiple RabbitMQ workers

Request-reply RabbitMQ messaging

Additional MCP server integrations

CI/CD with GitHub Actions

Prometheus & Grafana monitoring

Cloud deployment

Author

Abdul Momin Alam

Built as part of an AI Engineering Internship focused on Agentic AI,Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP),OpenAI Responses API, FastAPI, RabbitMQ, WebSockets, PostgreSQL andReact.