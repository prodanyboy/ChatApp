from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db" #nombre del file de la db

engine = create_engine( #esto es para crear el motor
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} #tenemos que poner el check...False solo porque es SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #esto crea la sesión la cuál nos sirve para guardar y borrar datos

Base = declarative_base() #esto hace que todos los modelos hereden de aquí (por eso se llama base)