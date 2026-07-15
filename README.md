# AI Developer Support Agent

An AI-powered developer support assistant built with the **OpenAI Responses API**, **Retrieval-Augmented Generation (RAG)**, **ChromaDB**, and the **Model Context Protocol (MCP)**.

The agent can answer technical questions from Supabase documentation, retrieve developer account information, create support tickets, and maintain context across a multi-turn conversation.

---

## Features

- Answers Supabase documentation questions using RAG
- Retrieves relevant document chunks from ChromaDB
- Includes source citations in documentation answers
- Uses an LLM to automatically select the correct tool
- Looks up developer accounts through a custom MCP server
- Creates and stores support tickets through MCP
- Supports multi-turn conversation memory
- Understands follow-up references such as:
  - “it”
  - “that account”
  - “the same user”
- Provides natural-language responses instead of raw JSON
- Includes an interactive terminal chat interface

---

## Example Conversation

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
Support ticket TKT-0013 was created successfully
for account ACC-1001.

You: What was the ticket ID?

Agent:
The ticket ID is TKT-0013.
```

---

## Architecture

```text
                         User
                           |
                           v
                        main.py
                           |
                           v
                        agent.py
                           |
                           v
                OpenAI Responses API
                  Intent and tool routing
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
   Direct response    RAG pipeline      MCP client
                           |                |
                           v                v
                       ChromaDB       Custom MCP server
                           |                |
                           v        +-------+--------+
                  Supabase docs      |                |
                                     v                v
                              Account lookup    Ticket creation
                                     |                |
                                     v                v
                              accounts.json     tickets.json
```

---

## How It Works

### 1. Tool Routing

The user’s message is sent to the OpenAI Responses API.

The model decides whether it should:

- answer directly,
- search documentation,
- look up an account, or
- create a support ticket.

### 2. RAG Documentation Search

For Supabase questions:

1. Documentation is divided into smaller chunks.
2. Each chunk is converted into an embedding.
3. The embeddings are stored in ChromaDB.
4. The user’s question is converted into an embedding.
5. The most relevant chunks are retrieved.
6. The model generates an answer using only the retrieved context.
7. Relevant source filenames are included in the response.

### 3. MCP Tools

Account lookup and ticket creation are exposed through a custom MCP server.

The agent communicates with the server using an asynchronous MCP client.

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

### 4. Conversation Memory

The project uses the Responses API’s response chaining to maintain multi-turn context.

This allows the agent to understand conversations such as:

```text
Show me account ACC-1001.
How much usage does it have left?
Create a ticket for it.
```

---

## Technologies

- Python
- OpenAI Responses API
- OpenAI Embeddings
- Retrieval-Augmented Generation
- ChromaDB
- Model Context Protocol
- AsyncIO
- JSON-based mock backend

---

## Project Structure

```text
ai-developer-support-agent/
|
|-- agent.py
|-- main.py
|-- tools.py
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
|-- examples/
|
|-- memory/
|
|-- test_agent.py
|-- test_tools.py
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/AbdulMominAlam/ai-developer-support-agent.git
cd ai-developer-support-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

Create a file named `.env` in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=your_openai_model
```

The `.env` file is excluded from Git and should never be committed.

---

## Prepare the RAG Database

The generated ChromaDB database and downloaded documentation are not included in the repository.

Place the documentation files inside:

```text
documents/
```

Then run:

```bash
python rag/ingest.py
```

This will:

- load the documents,
- split them into chunks,
- generate embeddings, and
- store them in ChromaDB.

---

## Run the Agent

Start the interactive terminal application:

```bash
python main.py
```

To close the application, type:

```text
exit
```

or:

```text
quit
```

---

## Run Tests

Test the complete agent:

```bash
python test_agent.py
```

Test the backend tools:

```bash
python test_tools.py
```

Test the MCP client directly:

```bash
python clients/mcp_client.py
```

---

## Available Tools

### `search_documentation`

Searches the indexed Supabase documentation using RAG.

### `get_account`

Returns account information including:

- name
- email
- plan
- account status
- monthly API usage
- monthly API limit

### `create_support_ticket`

Creates a support ticket containing:

- ticket ID
- account ID
- category
- description
- status
- creation timestamp

---

## Example Tool Routing

| User request | Selected path |
|---|---|
| “How do I reset a Supabase password?” | RAG documentation search |
| “Show me account ACC-1001.” | MCP account lookup |
| “Create a ticket for ACC-1002.” | MCP ticket creation |
| “Hello.” | Direct response |
| “How much usage does it have left?” | Conversation memory |

---

## Security

- API keys are loaded through environment variables.
- The `.env` file is excluded through `.gitignore`.
- No API keys or secrets should be hardcoded.
- MCP write operations should only be performed after clear user intent.
- The included accounts and tickets are mock data for demonstration purposes.

---

## Future Improvements

- Integrate GitHub’s official MCP server
- Add GitHub issue and repository tools
- Add a Streamlit or web interface
- Stream responses in real time
- Add persistent conversation storage
- Connect to a real database
- Add authentication and user permissions
- Improve logging and error handling
- Add automated unit and integration tests

---

## License

This project is licensed under the MIT License.

---

## Author

**Abdul Momin Alam**

GitHub: [AbdulMominAlam](https://github.com/AbdulMominAlam)