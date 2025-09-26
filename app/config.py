# app/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT / ".env")

class Settings:
    """Centraliza as configurações do aplicativo."""
    MONGO_URL: str = os.getenv("MONGO_URL", "")
    MONGO_DB: str = os.getenv("MONGO_DB", "chatdb")

    if not MONGO_URL:
        print(" Variável de ambiente 'MONGO_URL' não definida.")

settings = Settings()