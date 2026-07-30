import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const [sessionId, setSessionId] = useState(
    `session-${Date.now()}`
  );

  const [messages, setMessages] = useState([
    {
      sender: "agent",
      text: "Hello! How can I help you today?",
      tool: null,
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [streaming, setStreaming] = useState(false);

  // Used to automatically scroll to the newest message.
  const messagesEndRef = useRef(null);

  // Stores the active WebSocket connection.
  const socketRef = useRef(null);

  // Stores the index of the assistant message
  // currently receiving streamed text.
  const streamingMessageIndexRef = useRef(null);

  // Stores the tool being used for the current response.
  const currentToolRef = useRef(null);

  // Open the WebSocket connection when the page loads.
  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL;
    const apiToken = import.meta.env.VITE_API_TOKEN;

    if (!apiUrl) {
      console.error(
        "VITE_API_URL is missing from the frontend .env file."
      );
      return;
    }

    if (!apiToken) {
      console.error(
        "VITE_API_TOKEN is missing from the frontend .env file."
      );
      return;
    }

    // Convert the normal backend URL into a WebSocket URL.
    //
    // http://localhost:8000 becomes:
    // ws://localhost:8000
    //
    // https://example.com becomes:
    // wss://example.com
    const websocketUrl = apiUrl
      .replace(/^http:\/\//, "ws://")
      .replace(/^https:\/\//, "wss://")
      .replace(/\/$/, "");

    // Open the connection to the FastAPI WebSocket endpoint.
    const socket = new WebSocket(
      `${websocketUrl}/ws/chat?token=${encodeURIComponent(
        apiToken
      )}`
    );

    socketRef.current = socket;

    // Runs when the WebSocket connection is accepted.
    socket.onopen = () => {
      console.log("WebSocket connected.");
      setConnected(true);
    };

    // Runs whenever FastAPI sends a message.
    socket.onmessage = (event) => {
      let data;

      try {
        data = JSON.parse(event.data);
      } catch (error) {
        console.error(
          "Could not parse WebSocket message:",
          event.data,
          error
        );
        return;
      }

      console.log("WebSocket event:", data);

      // The backend sends this before it starts
      // producing the response.
      if (data.type === "response_started") {
        setLoading(true);
        setStreaming(true);

        currentToolRef.current = null;

        // Add one empty assistant message.
        //
        // Future text_delta events and tool badges
        // will update this same message.
        setMessages((currentMessages) => {
          const newMessages = [
            ...currentMessages,
            {
              sender: "agent",
              text: "",
              tool: null,
            },
          ];

          streamingMessageIndexRef.current =
            newMessages.length - 1;

          return newMessages;
        });

        return;
      }

      // The backend sends this when GPT selects a tool.
      if (data.type === "tool_started") {
        const selectedTool = data.tool || null;

        currentToolRef.current = selectedTool;

        // Attach the tool badge immediately to the
        // assistant message currently being streamed.
        setMessages((currentMessages) => {
          const messageIndex =
            streamingMessageIndexRef.current;

          if (
            messageIndex === null ||
            !currentMessages[messageIndex]
          ) {
            return currentMessages;
          }

          return currentMessages.map((message, index) => {
            if (index !== messageIndex) {
              return message;
            }

            return {
              ...message,
              tool: selectedTool,
            };
          });
        });

        return;
      }

      // Append each streamed text piece to the
      // same assistant message.
      if (data.type === "text_delta") {
        const delta =
          typeof data.delta === "string"
            ? data.delta
            : "";

        if (!delta) {
          return;
        }

        setMessages((currentMessages) => {
          const messageIndex =
            streamingMessageIndexRef.current;

          if (
            messageIndex === null ||
            !currentMessages[messageIndex]
          ) {
            return currentMessages;
          }

          return currentMessages.map((message, index) => {
            if (index !== messageIndex) {
              return message;
            }

            return {
              ...message,
              text: `${message.text || ""}${delta}`,
            };
          });
        });

        return;
      }

      // The backend sends this after the final text chunk.
      if (data.type === "response_completed") {
        // Save the completed values before clearing the refs.
        const completedMessageIndex =
          streamingMessageIndexRef.current;

        const completedTool =
          data.tool ?? currentToolRef.current ?? null;

        setMessages((currentMessages) => {
          if (
            completedMessageIndex === null ||
            !currentMessages[completedMessageIndex]
          ) {
            return currentMessages;
          }

          return currentMessages.map((message, index) => {
            if (index !== completedMessageIndex) {
              return message;
            }

            return {
              ...message,
              tool: completedTool,
            };
          });
        });

        streamingMessageIndexRef.current = null;
        currentToolRef.current = null;

        setStreaming(false);
        setLoading(false);

        return;
      }

      // Display backend errors inside the chat.
      if (data.type === "error") {
        const errorMessage =
          data.message ||
          "An unexpected error occurred.";

        const currentStreamingIndex =
          streamingMessageIndexRef.current;

        setMessages((currentMessages) => {
          // If an empty streamed assistant message already exists,
          // place the error inside that same bubble.
          if (
            currentStreamingIndex !== null &&
            currentMessages[currentStreamingIndex]
          ) {
            return currentMessages.map(
              (message, index) => {
                if (index !== currentStreamingIndex) {
                  return message;
                }

                return {
                  ...message,
                  text: errorMessage,
                  tool:
                    message.tool ||
                    currentToolRef.current,
                };
              }
            );
          }

          // Otherwise, add a new error message.
          return [
            ...currentMessages,
            {
              sender: "agent",
              text: errorMessage,
              tool: null,
            },
          ];
        });

        streamingMessageIndexRef.current = null;
        currentToolRef.current = null;

        setStreaming(false);
        setLoading(false);
      }
    };

    // Runs if the browser encounters a WebSocket error.
    socket.onerror = (error) => {
      console.error("WebSocket error:", error);

      streamingMessageIndexRef.current = null;
      currentToolRef.current = null;

      setStreaming(false);
      setLoading(false);
    };

    // Runs when the WebSocket connection closes.
    socket.onclose = (event) => {
      console.log(
        "WebSocket disconnected:",
        event.code,
        event.reason
      );

      setConnected(false);

      streamingMessageIndexRef.current = null;
      currentToolRef.current = null;

      setStreaming(false);
      setLoading(false);
    };

    // Close the connection when the component is removed
    // or when the page is refreshed.
    return () => {
      if (
        socket.readyState === WebSocket.OPEN ||
        socket.readyState === WebSocket.CONNECTING
      ) {
        socket.close();
      }
    };
  }, []);

  // Automatically scroll when messages or loading changes.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const sendMessage = () => {
    const trimmedInput = input.trim();

    if (
      trimmedInput === "" ||
      loading ||
      !connected
    ) {
      return;
    }

    const socket = socketRef.current;

    // Make sure the WebSocket is open
    // before sending a message.
    if (
      !socket ||
      socket.readyState !== WebSocket.OPEN
    ) {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          sender: "agent",
          text: "The WebSocket connection is not ready.",
          tool: null,
        },
      ]);

      return;
    }

    const userMessage = {
      sender: "user",
      text: trimmedInput,
      tool: null,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setInput("");
    setLoading(true);
    setStreaming(false);

    streamingMessageIndexRef.current = null;
    currentToolRef.current = null;

    // Convert the JavaScript object into JSON text
    // and send it through the WebSocket.
    socket.send(
      JSON.stringify({
        message: trimmedInput,
        session_id: sessionId,
      })
    );
  };

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  const startNewChat = () => {
    // Create a new conversation session.
    //
    // The WebSocket connection itself stays open.
    setSessionId(`session-${Date.now()}`);

    setMessages([
      {
        sender: "agent",
        text: "Hello! How can I help you today?",
        tool: null,
      },
    ]);

    streamingMessageIndexRef.current = null;
    currentToolRef.current = null;

    setInput("");
    setLoading(false);
    setStreaming(false);
  };

  const formatToolName = (tool) => {
    const toolNames = {
      get_account: "Account Lookup",
      create_support_ticket: "Support Ticket",
      search_documentation: "Documentation Search",
      search_github_repositories:
        "GitHub Repository Search",
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

            <p>
              Connected using WebSockets, PostgreSQL and
              MCP tools
            </p>
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
          <span
            className={
              connected
                ? "status-dot"
                : "status-dot disconnected"
            }
          ></span>

          <span>
            {connected ? "Connected" : "Disconnected"} |
            Session ID: {sessionId}
          </span>
        </div>

        <main className="messages">
          {messages.map((message, index) => (
            <div
              key={`${message.sender}-${index}`}
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
                      <span
                        className="tool-badge"
                        key={toolName}
                      >
                        {formatToolName(toolName)}
                      </span>
                    ))}
                  </div>
                )}

                <div>{message.text}</div>
              </div>
            </div>
          ))}

          {loading && !streaming && (
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
            disabled={loading || !connected}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
          />

          <button
            type="button"
            className="send-button"
            onClick={sendMessage}
            disabled={
              loading ||
              !connected ||
              input.trim() === ""
            }
          >
            {loading ? "Sending" : "Send"}
          </button>
        </footer>
      </div>
    </div>
  );
}

export default App;