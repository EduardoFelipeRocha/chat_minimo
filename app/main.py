# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes import messages
from app.config import settings
from app.database import get_db

app = FastAPI(title="FastAPI Chat + MongoDB Atlas")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conecta ao banco de dados na inicialização
@app.on_event("startup")
async def startup_event():
    get_db()

# Monta o diretório de arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("app/static/index.html")

# Inclui as rotas do módulo messages
app.include_router(messages.router)