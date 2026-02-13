from sqlalchemy.orm import Session
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, List
from database import engine, SessionLocal
import models, schemas
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine) #esto va a crear las tablas en la db si es que no hay

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConnectionManager:
    def __init__(self):
        self.active_connections = Dict[str, List[WebSocket]] ={}
    async def connect(self, websocket: WebSocket, room_name: str):
        await websocket.accept()
        if room_name not in self.active_connections:
            self.active_connections[room_name] = []
        self.active_connections[room_name].apppend(websocket)
    def disconnect(self, websocket: WebSocket, room_name: str):
        if room_name in self.active_connections:
            self.active_connections[room_name].remove(websocket)
    async def broadcast(self, message: str, room_name: str):
        if room_name in self.active_connections:
            for connection in self.active_connections[room_name]:
                await connection.send_text(message)

manager = ConnectionManager()

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    return {"message": "Login exitoso", "username": db_user.username}

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username) #esto y lo de if db_user es para verificar si el usuario ya existe y si existe, le damos HTTPException

    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe, por favor ingresar otro usuario")
    
    new_user = models.User(username= user.username, password=user.password) #en este caso, no vamos a encriptar la contraseña porque es un proyecto sencillo

    db.add(new_user) #añado al usuario a la db
    db.commit() # esto es para confirmar cambios
    db.refresh(new_user) # refresheo al user para obtener su id

    return new_user

@app.websocket("/ws/{room_name}/{username}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    
    try:
        while True:
               data = await websocket.receive_text() #esperamos para recibir el texto (por eso ponemos await)
               await manager.broadcast(f"Usuario {client_id} dice: {data}") #guardamos la id del user en una variable llamada "data"
            
    except Exception:
        manager.disconnect(websocket)
        await manager.broadcast(f"El Usuario {client_id} ha abandonado el chat")