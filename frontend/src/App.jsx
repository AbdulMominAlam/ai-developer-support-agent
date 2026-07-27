import { useState } from "react";
import "./App.css";

function App() {
  // Stores all messages shown in the chat
  const [messages, setMessages] = useState([
    {
      sender: "agent",
      text: "Hello! How can I help you today?",
    },
  ]);

  // Stores the text currently typed by the user
  const [input, setInput] = useState("");

  const sendMessage = () => {
    // Do not send an empty message
    if (input.trim() === "") {
      return;
    }

    const userMessage = {
      sender: "user",
      text: input,
    };

    const temporaryAgentMessage = {
      sender: "agent",
      text: "This will eventually come from our AI backend.",
    };

    // Add both the user's message and the temporary AI response
    setMessages([
      ...messages,
      userMessage,
      temporaryAgentMessage,
    ]);

    // Clear the input box
    setInput("");
  };

  const handleKeyDown = (event) => {
    // Send the message when Enter is pressed
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <h1>AI Developer Support Agent</h1>

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
              {message.text}
            </div>
          ))}
        </div>

        <div className="input-area">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
          />

          <button type="button" onClick={sendMessage}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;