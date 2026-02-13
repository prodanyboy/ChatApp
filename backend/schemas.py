#es el cómo nuestros datos viajan por el internet (por los json)

from pydantic import BaseModel

class UserCreate(BaseModel): #lo creamos para que el usuario solo pueda ingresar str al crear un user
    username: str
    password: str

class UserResponse(BaseModel): #esto es lo que le vamos a devolver al usuario (sin la password para que no sea tan vulnerable)
    id: int
    username: str

    class Config:
        orm_mode = True