import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [step, setStep] = useState("login"); 
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [room, setRoom] = useState("");
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const socketRef = useRef(null);
  const messagesEndRef = useRef(null);
  const [isRegistering, setIsRegistering] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (response.ok) {
        setStep("room");
      } else {
        alert("Error: Usuario o contraseña incorrectos");
      }
    } catch (error) {
      alert("Error de conexión con el backend");
    }
  };

  const handleRegister = async (e) => {
  e.preventDefault();
  try {
    const response = await fetch("http://localhost:8000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      alert("¡Usuario creado con éxito! Ahora inicia sesión.");
      setIsRegistering(false);
    } else {
      alert("Error: El usuario ya existe o hubo un fallo.");
    }
  } catch (error) {
    alert("Error de conexión");
  }
};

  const joinRoom = (e) => {
    e.preventDefault();
    if (!room) return;
    const ws = new WebSocket(`ws://localhost:8000/ws/${room}/${username}`);
    ws.onopen = () => {
      setStep("chat");
    };
    ws.onmessage = (event) => {
      setMessages((prev) => [...prev, event.data]);
    };
    socketRef.current = ws;
  };

  const sendMessage = (e) => {
    e.preventDefault();
    if (socketRef.current && inputValue) {
      socketRef.current.send(inputValue);
      setInputValue("");
    }
  };

  const logout = () => {
    if (socketRef.current) socketRef.current.close();
    setStep("login");
    setMessages([]);
    setUsername("");
    setPassword("");
  };

  return (
    <div className="app-container">
      
      {/* LOGIN */}
      {step === "login" && (
    <div className="login-container">
      <h1>{isRegistering ? "Crear Cuenta" : "Bienvenido 👋"}</h1>
      <p>{isRegistering ? "Regístrate para empezar" : "Inicia sesión para chatear"}</p>

      <form onSubmit={isRegistering ? handleRegister : handleLogin}>
        <input 
          placeholder="Usuario" 
          value={username} 
          onChange={(e) => setUsername(e.target.value)} 
          required 
        />
        <input 
          type="password" 
          placeholder="Contraseña" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
          required 
        />
        <button type="submit">
          {isRegistering ? "Registrarse" : "Entrar"}
        </button>
      </form>

      {/* Botón Login y Registro */}
      <p style={{marginTop: "15px", fontSize: "14px"}}>
        {isRegistering ? "¿Ya tienes cuenta? " : "¿No tienes cuenta? "}
        <span 
          onClick={() => setIsRegistering(!isRegistering)}
          style={{color: "#00a884", cursor: "pointer", fontWeight: "bold"}}
        >
          {isRegistering ? "Inicia Sesión" : "Regístrate aquí"}
        </span>
      </p>
    </div>
  )}

      {/* SALA */}
      {step === "room" && (
        <div className="room-container">
          <h2>Hola, {username}</h2>
          <p>¿A qué sala quieres entrar?</p>
          <form onSubmit={joinRoom}>
            <input 
              placeholder="Ej: Futbol, Cine, Trabajo..." 
              value={room} 
              onChange={(e) => setRoom(e.target.value)} 
              required 
            />
            <button type="submit">Unirse a la Sala</button>
          </form>
        </div>
      )}

      {/* CHAT */}
      {step === "chat" && (
        <div className="chat-container">
          {/* Cabecera */}
          <div className="chat-header">
            <span>Sala: {room}</span>
            <button onClick={logout} className="logout-btn">Salir</button>
          </div>

          {/* Área de Mensajes */}
          <div className="messages-area">
            {messages.map((msg, index) => {
              const parts = msg.split(':');
              const sender = parts[0]; 
              const isMe = sender === username;
              
              const isSystem = msg.includes("🔵") || msg.includes("🔴");

              return (
                <div 
                  key={index} 
                  className={`message-bubble ${isSystem ? "system-msg" : (isMe ? "my-message" : "other-message")}`}
                  style={isSystem ? {alignSelf: "center", background: "transparent", color: "#666", fontSize: "12px"} : {}}
                >
                  {!isMe && !isSystem && <span className="message-username">{sender}</span>}
                  {isSystem ? msg : parts.slice(1).join(':')}
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={sendMessage} className="input-area">
            <input 
              value={inputValue} 
              onChange={(e) => setInputValue(e.target.value)} 
              placeholder="Escribe un mensaje..." 
            />
            <button type="submit">➤</button>
          </form>
        </div>
      )}
    </div>
  )
}

export default App