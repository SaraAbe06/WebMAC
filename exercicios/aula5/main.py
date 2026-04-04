from typing import Annotated
from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class Usuario(BaseModel):
    nome: str
    senha: str 
    bio: str | None = ""

usuarios=[]

@app.get("/",response_class=HTMLResponse)
def retorna_forms_cadastro(request: Request):
    return templates.TemplateResponse(request=request, name="cadastro.html")

@app.post("/users")
def criar_usuario(user: Usuario):
    usuarios.append(user)
    return {"usuario": user.nome}

@app.get("/login",response_class=HTMLResponse)
def retorna_forms_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login(usuario: Usuario, response: Response):
    usuario_encontrado = None
    for u in usuarios:
        if u.nome == usuario.nome and u.senha==usuario.senha:
            usuario_encontrado = u
            break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    response.set_cookie(key="session_user", value=usuario.nome)
    return {"message": "Logado com sucesso"}


def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado."
        )
    
    user = next((u for u in usuarios if u.nome == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user

@app.get("/home")
def show_profile(request: Request, user: Usuario = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request, 
        name="perfil.html", 
        context={"nome": user.nome, "bio": user.bio}
    )
