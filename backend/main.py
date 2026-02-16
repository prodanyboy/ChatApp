from sqlalchemy.orm import Session
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, List
from database import engine, SessionLocal
import models, schemas
from pydantic import BaseModel

#usar "pip install -r requirements.txt" en su propio entorno virtual para tener las librerías

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_name: str):
        await websocket.accept()
        if room_name not in self.active_connections:
            self.active_connections[room_name] = []
        self.active_connections[room_name].append(websocket)

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
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    if db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    return {"message": "Login exitoso", "username": db_user.username}

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe, por favor ingresar otro usuario")
    
    new_user = models.User(username= user.username, password=user.password) 

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app.delete("/users/{username}")
def delete_user(username: str, db: Session = Depends(get_db)):
    user_to_delete = db.query(models.User).filter(models.User.username == username).first()
    
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    
    db.delete(user_to_delete)
    db.commit()
    
    return {"message": f"El usuario '{username}' ha sido eliminado con éxito"}

@app.websocket("/ws/{room_name}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, username: str, db: Session = Depends(get_db)):
    await manager.connect(websocket, room_name)
    
    messages = db.query(models.Message).filter(models.Message.room == room_name).all()
    
    for msg in messages:
        await websocket.send_text(f"{msg.sender}:{msg.content}")
        
    await manager.broadcast(f"🔵 {username} se unió a la sala.", room_name)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            new_message = models.Message(room=room_name, sender=username, content=data)
            db.add(new_message)
            db.commit()
            
            await manager.broadcast(f"{username}:{data}", room_name)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_name)
        await manager.broadcast(f"🔴 {username} salió de la sala.", room_name)