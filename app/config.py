import os

from dotenv import load_dotenv

load_dotenv()


def get_postgres_uri() -> str:
    uri = os.environ.get("DATABASE_URL")
    if not uri:
        raise RuntimeError("DATABASE_URL no está definida (revisa tu archivo .env)")
    return uri


def get_allowed_origins() -> list[str]:
    """Orígenes permitidos por CORS, configurables vía ALLOWED_ORIGINS (separados por coma)."""
    origins = os.environ.get("ALLOWED_ORIGINS", "*")
    return [origin.strip() for origin in origins.split(",")]
