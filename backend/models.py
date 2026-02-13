# es el cómo los datos se guardan en la base de datos (las tablas)

from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) # lo ponemos como primary key para que pueda ser pulleado en otras tablas
    username = Column(String, unique=True, index=True) #lo hacemos unico para que haya 1 de cada 1
    password = Column(String)

class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index= True)
    message = Column(String)