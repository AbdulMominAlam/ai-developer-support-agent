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
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);

  // Tracks whether text is currently being streamed.
  //
  // We use this to avoid showing the thinking dots
  // underneath the streamed assistant message.
  const [streaming, setStreaming] = useState(false);

  // Used to automatically scroll to the newest message.
  const messagesEndRef = useRef(null);

  // Stores the WebSocket connection.
  //
  // useRef is used because changing socketRef.current
  // should not cause the component to render again.
  const socketRef = useRef(null);

  // Stores the index of the assistant message
  // currently receiving streamed text.
  //
  // All incoming text_delta events are appended
  // to this same message.
  const streamingMessageIndexRef = useRef(null);

  // Open the WebSocket connection when the page loads.
  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL;
    const apiToken = import.meta.env.VITE_API_TOKEN;

    // Convert the normal backend URL into a WebSocket URL.
    //
    // http://localhost:8000 becomes:
    // ws://localhost:8000
    //
    // https://example.com becomes:
    // wss://example.com
    const websocketUrl = apiUrl
      .replace("http://", "ws://")
      .replace("https://", "wss://");

    // Open the connection to the FastAPI WebSocket endpoint.
    //
    // The API token is sent as a query parameter because
    // the browser WebSocket API cannot easily send a custom
    // Authorization header.
    const socket = new WebSocket(
      `${websocketUrl}/ws/chat?token=${encodeURIComponent(
        apiToken
      )}`
    );

    // Store the socket so sendMessage() can use it later.
    socketRef.current = socket;

    // Runs when the WebSocket connection is accepted.
    socket.onopen = () => {
      console.log("WebSocket connected.");
      setConnected(true);
    };

    // Runs whenever FastAPI sends a message.
    socket.onmessage = (event) => {
      // WebSocket messages arrive as text.
      // Convert the JSON text into a JavaScript object.
      const data = JSON.parse(event.data);

      console.log("WebSocket event:", data);

      // The backend sends this event before it starts
      // producing the answer.
      if (data.type === "response_started") {
        setLoading(true);
        setStreaming(true);

        // Add one empty assistant message.
        // Future text_delta events will append text
        // to this same message.
        setMessages((currentMessages) => {
          const newMessages = [
            ...currentMessages,
            {
              sender: "agent",
              text: "",
              tool: null,
            },
          ];

          // Save the position of the empty assistant message.
          streamingMessageIndexRef.current =
            newMessages.length - 1;

          return newMessages;
        });

        return;
      }

      // The backend sends one text_delta event
      // for every streamed piece of text.
      if (data.type === "text_delta") {
        setMessages((currentMessages) => {
          const updatedMessages = [...currentMessages];

          const messageIndex =
            streamingMessageIndexRef.current;

          // Safety check in case no streaming message exists.
          if (
            messageIndex === null ||
            !updatedMessages[messageIndex]
          ) {
            return currentMessages;
          }

          // Copy the current assistant message
          // and append the newest text chunk.
          updatedMessages[messageIndex] = {
            ...updatedMessages[messageIndex],
            text:
              updatedMessages[messageIndex].text +
              data.delta,
          };

          return updatedMessages;
        });

        return;
      }

      // The backend sends this after the final chunk.
      if (data.type === "response_completed") {
        setMessages((currentMessages) => {
          const updatedMessages = [...currentMessages];

          const messageIndex =
            streamingMessageIndexRef.current;

          // Add the tool badge to the same message
          // that received the streamed text.
          if (
            messageIndex !== null &&
            updatedMessages[messageIndex]
          ) {
            updatedMessages[messageIndex] = {
              ...updatedMessages[messageIndex],
              tool: data.tool,
            };
          }

          return updatedMessages;
        });

        // No more chunks will be added to this message.
        streamingMessageIndexRef.current = null;

        setStreaming(false);
        setLoading(false);

        return;
      }

      // Display backend errors inside the chat.
      if (data.type === "error") {
        setMessages((currentMessages) => [
          ...currentMessages,
          {
            sender: "agent",
            text:
              data.message ||
              "An unexpected error occurred.",
          },
        ]);

        streamingMessageIndexRef.current = null;
        setStreaming(false);
        setLoading(false);
      }
    };

    // Runs if the browser encounters a socket error.
    socket.onerror = (error) => {
      console.error("WebSocket error:", error);

      streamingMessageIndexRef.current = null;
      setStreaming(false);
      setLoading(false);
    };

    // Runs when the connection closes.
    socket.onclose = (event) => {
      console.log(
        "WebSocket disconnected:",
        event.code,
        event.reason
      );

      setConnected(false);
      streamingMessageIndexRef.current = null;
      setStreaming(false);
      setLoading(false);
    };

    // Close the connection when this component is removed
    // or when the page is refreshed.
    return () => {
      socket.close();
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

    if (trimmedInput === "" || loading) {
      return;
    }

    const socket = socketRef.current;

    // Make sure the socket exists and is connected
    // before trying to send a message.
    if (
      !socket ||
      socket.readyState !== WebSocket.OPEN
    ) {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          sender: "agent",
          text: "The WebSocket connection is not ready.",
        },
      ]);

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

    // WebSockets send text.
    //
    // JSON.stringify converts the JavaScript object
    // into JSON text before sending it to FastAPI.
    socket.send(
      JSON.stringify({
        message: trimmedInput,
        session_id: sessionId,
      })
    );
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  const startNewChat = () => {
    // Create a new application session.
    //
    // The WebSocket connection itself stays open.
    // Only the conversation session ID changes.
    setSessionId(`session-${Date.now()}`);

    setMessages([
      {
        sender: "agent",
        text: "Hello! How can I help you today?",
      },
    ]);

    streamingMessageIndexRef.current = null;

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

          {/* Show thinking dots only before streaming begins. */}
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
            disabled={loading || !connected}
          >
            {loading ? "Sending" : "Send"}
          </button>
        </footer>
      </div>
    </div>
  );
}

export default App;