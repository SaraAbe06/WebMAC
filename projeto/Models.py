from typing import List, Optional 
from sqlmodel import Field, Relationship, SQLModel

class Livro(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    nota: float
    autor_id: int = Field(foreign_key="autor.id")

    autor: Optional["Autor"]= Relationship(back_populates="livros")

class Autor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)   
    nome: str 

    livros: List["Livro"] = Relationship(back_populates="autor")