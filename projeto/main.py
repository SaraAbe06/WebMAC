from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from sqlmodel import Session, desc, select, SQLModel, create_engine
from Models import Livro,Autor
from contextlib import asynccontextmanager

@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

arquivo_sqlite = "projetinho_mybookshelf.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app= FastAPI(lifespan=initFunction)

templates = Jinja2Templates(directory="Templates")

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"pagina": "/home"})

@app.get("/home", response_class=HTMLResponse)
async def pag1(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/home"})
    return templates.TemplateResponse(request, "home.html")

@app.get("/AdicionarLivro", response_class=HTMLResponse)
async def pag2(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/AdicionarLivro"})
    return templates.TemplateResponse(request, "pagina_adicionar.html")

@app.get("/DeletarLivro", response_class=HTMLResponse)
async def pag3(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/DeletarLivro"})
    return templates.TemplateResponse(request, "pagina_deletar.html")

@app.get("/AtualizarLivro", response_class=HTMLResponse)
async def pag4(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/AtualizarLivro"})
    return templates.TemplateResponse(request, "pagina_atualizar.html")


@app.post("/AdicionarLivro", response_class=HTMLResponse)
def criar_livro(nome: str = Form(...), nome_autor: str=Form(...), nota: float=Form(...)):
    with Session(engine) as session:
        nome=nome.strip()
        nome_autor=nome_autor.strip()

        query_autor=select(Autor).where(Autor.nome==nome_autor)
        autor=session.exec(query_autor).first()
        if (not autor):
            autor=Autor(nome=nome_autor)
            session.add(autor)
            session.commit()
            session.refresh(autor)

        query_livro=select(Livro).where(Livro.nome==nome,Livro.autor_id==autor.id)
        livro=session.exec(query_livro).first()
        if livro:
            return HTMLResponse(content=f"<p>O livro {nome} de {nome_autor} já existia!</p>")
        
        novo_livro=Livro(nome=nome,nota=nota,autor_id=autor.id)
        session.add(novo_livro)
        session.commit()
        session.refresh(novo_livro)

        return HTMLResponse(content=f"<p>O livro {nome} do(a) autor(a) {nome_autor} foi registrado!</p>")

@app.delete("/DeletarLivro", response_class=HTMLResponse)
def deletar_aluno(nome: str, nome_autor: str):
    with Session(engine) as session:
        nome=nome.strip()
        nome_autor=nome_autor.strip()

        query_autor=select(Autor).where(Autor.nome==nome_autor)
        autor=session.exec(query_autor).first()
        if (not autor):
            return HTMLResponse(content=f"<p>O autor não foi encontrado</p>")

        query_livro = select(Livro).where(Livro.nome==nome, Livro.autor_id==autor.id)
        livro = session.exec(query_livro).first()
        if (not livro):
            return HTMLResponse(content=f"<p>O livro não foi encontrado</p>")
        
        session.delete(livro)
        session.commit()
        return HTMLResponse(content=f"<p>O livro {nome} do(a) autor(a) {nome_autor} foi deletado!</p>")
    
@app.put("/AtualizaLivro", response_class=HTMLResponse)
def atualizar_aluno(nome: str = Form(...), nome_autor: str = Form(...), nova_nota: float = Form(...)):
    with Session(engine) as session:
        nome=nome.strip()
        nome_autor=nome_autor.strip()
    
        query_autor=select(Autor).where(Autor.nome==nome_autor)
        autor=session.exec(query_autor).first()
        if (not autor):
            return HTMLResponse(content=f"<p>O autor não foi encontrado</p>")
        
        query_livro = select(Livro).where(Livro.nome==nome, Livro.autor_id==autor.id)
        livro = session.exec(query_livro).first()
        if (not livro):
            return HTMLResponse(content=f"<p>O livro não foi encontrado</p>")
        
        nota_antiga = livro.nota
        livro.nota = nova_nota
        session.commit()
        session.refresh(livro)
        return HTMLResponse(content=f"<p>O livro {nome} do(a) autor(a) {nome_autor} com nota {nota_antiga} foi atualizado para nota {nova_nota}!</p>")

def buscar_livros(page: int=1, nome_livro: str | None = None, nome_autor: str | None = None):
    limite_itens=10
    with Session(engine) as session:

        offset=(page-1)*limite_itens
        query=select(Livro,Autor).join(Autor, Livro.autor_id==Autor.id)

        if nome_livro: 
            nome_livro=nome_livro.strip()
            query=query.where(Livro.nome==nome_livro).order_by(desc(Livro.nota))
        if nome_autor:
            nome_autor=nome_autor.strip()
            query=query.where(Autor.nome==nome_autor).order_by(desc(Livro.nota))

        
        query=query.order_by(desc(Livro.nota)).offset(offset).limit(limite_itens+1)
        res=session.exec(query).all()

        if limite_itens<len(res):
            flag_proxima=True
        else:
            flag_proxima=False
    
        return res[:limite_itens],flag_proxima
    
@app.get("/Rank", response_class=HTMLResponse)
def lista(request: Request,page:int=1, nome_livro: str | None=None, nome_autor: str | None=None):
    livros,flag_proxima = buscar_livros(page,nome_livro, nome_autor)
   
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/Rank", "flag_proxima":flag_proxima,"page":page,"nome_livro": nome_livro,"nome_autor": nome_autor})
    return templates.TemplateResponse(request, "pagina_rank.html", {"flag_proxima":flag_proxima,"page":page,"livros": livros,"nome_livro": nome_livro,"nome_autor": nome_autor})