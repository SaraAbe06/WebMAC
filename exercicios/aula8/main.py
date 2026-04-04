from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from Models import Objeto
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select

@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=initFunction)

arquivo_sqlite = "aula8.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app.mount("/static", StaticFiles(directory="Templates"), name="static")
    
@app.get("/", response_class=HTMLResponse)
def busca(request: Request):
    return templates.TemplateResponse(request, "index.html", {"pagina": "curtidas"})

@app.get("/curtidas")
def curtidas(request: Request):
    with Session(engine) as session:
        query=select(Objeto)
        query=session.exec(query).first()

        if not query:
            query=Objeto(quantidade=0)
            session.add(query)
            session.commit()
            session.refresh(query)

    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/curtidas"})
    return templates.TemplateResponse(request, "curtidas.html", {"contador": query})

@app.get("/jupiter")
def curtidas(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/jupiter"})
    return templates.TemplateResponse(request, "jupiter.html")

@app.get("/siteprof")
def curtidas(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/siteprof"})
    return templates.TemplateResponse(request, "siteprof.html")



@app.post("/curtidas", response_class=HTMLResponse)
def curtir():
    with Session(engine) as session:
        query=session.exec(select(Objeto)).first()

        if not query:
            query=Objeto(quantidade=1)
            session.add(query)
        else:
            query.quantidade+=1
            session.add(query)
        session.commit()
        session.refresh(query)

        return HTMLResponse(content=str(query.quantidade))
    
@app.delete("/curtidas", response_class=HTMLResponse)
def deletar():
    with Session(engine) as session:
        query = session.exec(select(Objeto)).first()
        query.quantidade=0
        session.add(query)
        session.commit()
        session.refresh(query)
        return HTMLResponse(content=str(query.quantidade))
