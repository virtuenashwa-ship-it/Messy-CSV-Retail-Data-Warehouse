from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "retail_warehouse.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

RAW_DIR.mkdir(parents=True, exist_ok=True)
