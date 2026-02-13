import { useState, useEffect } from 'react'

function App() {
  const [clientId] = useState(Math.floor(Date.now() / 1000));
  
  const [messages, setMessages] = useState([]);
  
  const [inputValue, setInputValue] = useState("");
  
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

    newSocket.onopen = () => {
      console.log("Conectado al WS");
    };

    newSocket.onmessage = (event) => {
      setMessages((prev) => [...prev, event.data]);
    };

    setSocket(newSocket);

    return () => newSocket.close();
  }, []);

  const sendMessage = (e) => {
    e.preventDefault();
    if (socket && inputValue) {
      socket.send(inputValue);
      setInputValue("");
    }
  };

  return (
    <div className="chat-container">
      <h1>Chat React - ID: {clientId}</h1>
      
      <div className="messages-list">
        {messages.map((msg, index) => (
          <div key={index} className="message-item">
            {msg}
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage}>
        <input 
          type="text" 
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Escribe un mensaje..."
        />
        <button type="submit">Enviar</button>
      </form>
    </div>
  )
}

export default App