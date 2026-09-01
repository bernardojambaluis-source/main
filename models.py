from sqlalchemy import Column, Integer, String, Text

from database import Base


class Obra(Base):
    __tablename__ = "obras"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    categoria = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    imagem = Column(String(500), nullable=False)


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)