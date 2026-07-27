import { useState } from "react";
import api from "./api";
import "./App.css";

function App() {
  // Create one session ID when the page first loads.
  const [sessionId, setSessionId] = useState(
    `session-${Date.now()}`
  );

  // Stores all messages displayed in the chat.
  const [messages, setMessages] = useState([
    {
      sender: "agent",
      text: "Hello! How can I help you today?",
    },
  ]);

  // Stores the text currently typed by the user.
  const [input, setInput] = useState("");

  // Prevents multiple messages from being sent at the same time.
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const trimmedInput = input.trim();

    // Do not send an empty message or another message while loading.
    if (trimmedInput === "" || loading) {
      return;
    }

    const userMessage = {
      sender: "user",
      text: trimmedInput,
    };

    // Immediately display the user's message.
    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setInput("");
    setLoading(true);

    try {
      // Send the user's message and session ID to FastAPI.
      const response = await api.post("/chat", {
        message: trimmedInput,
        session_id: sessionId,
      });

      const agentMessage = {
        sender: "agent",
        text: response.data.answer,
        tool: response.data.tool,
      };

      // Display the answer returned by FastAPI.
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
    // A new session ID starts a completely separate conversation.
    setSessionId(`session-${Date.now()}`);

    setMessages([
      {
        sender: "agent",
        text: "Hello! How can I help you today?",
      },
    ]);

    setInput("");
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <div>
            <h1>AI Developer Support Agent</h1>
            <p>Session: {sessionId}</p>
          </div>

          <button
            type="button"
            className="new-chat-button"
            onClick={startNewChat}
            disabled={loading}
          >
            New Chat
          </button>
        </div>

        <div className="messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={
                message.sender === "user"
                  ? "message user-message"
                  : "message agent-message"
              }
            >
              {message.tool && (
                <div className="tool-name">
                  Tool used:{" "}
                  {Array.isArray(message.tool)
                    ? message.tool.join(", ")
                    : message.tool}
                </div>
              )}

              <div>{message.text}</div>
            </div>
          ))}

          {loading && (
            <div className="message agent-message">
              Thinking...
            </div>
          )}
        </div>

        <div className="input-area">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            disabled={loading}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
          />

          <button
            type="button"
            onClick={sendMessage}
            disabled={loading}
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;