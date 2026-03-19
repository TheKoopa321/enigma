import os
from pathlib import Path

APP_NAME = "Enigma"

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR.parent.parent / "data"))
DB_PATH = DATA_DIR / "enigma.db"
