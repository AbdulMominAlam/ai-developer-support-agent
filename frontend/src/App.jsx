import { useEffect, useRef, useState } from "react";
import api from "./api";
import "./App.css";

function App() {
  const [sessionId, setSessionId] = useState(
    `session-${Date.now()}`
  );

  const [messages, setMessages] = useState([
    {
      sender: "agent",
      text: "Hello! How can I help you today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Used to automatically scroll to the newest message.
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const sendMessage = async () => {
    const trimmedInput = input.trim();

    if (trimmedInput === "" || loading) {
      return;
    }

    const userMessage = {
      sender: "user",
      text: trimmedInput,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await api.post("/chat", {
        message: trimmedInput,
        session_id: sessionId,
      });

      const agentMessage = {
        sender: "agent",
        text: response.data.answer,
        tool: response.data.tool,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        agentMessage,
      ]);
    } catch (error) {
      console.error("API error:", error);

      let errorMessage =
        "Unable to connect to the AI Developer Support Agent.";

      if (error.response?.status === 401) {
        errorMessage = "Invalid API token.";
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          sender: "agent",
          text: errorMessage,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  const startNewChat = () => {
    setSessionId(`session-${Date.now()}`);

    setMessages([
      {
        sender: "agent",
        text: "Hello! How can I help you today?",
      },
    ]);

    setInput("");
  };

  const formatToolName = (tool) => {
    const toolNames = {
      get_account: "Account Lookup",
      create_support_ticket: "Support Ticket",
      search_documentation: "Documentation Search",
      search_github_repositories: "GitHub Repository Search",
      list_github_issues: "GitHub Issue Search",
      read_github_file: "GitHub File Reader",
    };

    return toolNames[tool] || tool;
  };

  return (
    <div className="app">
      <div className="chat-container">
        <header className="chat-header">
          <div>
            <h1>AI Developer Support Agent</h1>
            <p>Connected to FastAPI, PostgreSQL and MCP tools</p>
          </div>

          <button
            type="button"
            className="new-chat-button"
            onClick={startNewChat}
            disabled={loading}
          >
            New Chat
          </button>
        </header>

        <div className="session-status">
          <span className="status-dot"></span>
          <span>Active session</span>
        </div>

        <main className="messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={
                message.sender === "user"
                  ? "message-row user-row"
                  : "message-row agent-row"
              }
            >
              <div
                className={
                  message.sender === "user"
                    ? "message user-message"
                    : "message agent-message"
                }
              >
                {message.tool && (
                  <div className="tool-badges">
                    {(Array.isArray(message.tool)
                      ? message.tool
                      : [message.tool]
                    ).map((toolName) => (
                      <span className="tool-badge" key={toolName}>
                        {formatToolName(toolName)}
                      </span>
                    ))}
                  </div>
                )}

                <div>{message.text}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row agent-row">
              <div className="message agent-message thinking-message">
                <span className="thinking-dot"></span>
                <span className="thinking-dot"></span>
                <span className="thinking-dot"></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef}></div>
        </main>

        <footer className="input-area">
          <input
            type="text"
            placeholder="Ask about accounts, documentation, tickets or GitHub..."
            value={input}
            disabled={loading}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
          />

          <button
            type="button"
            className="send-button"
            onClick={sendMessage}
            disabled={loading}
          >
            {loading ? "Sending" : "Send"}
          </button>
        </footer>
      </div>
    </div>
  );
}

export default App;