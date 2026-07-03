"""app/entrypoints/routers/health.py"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    """Verifica que la API esté disponible."""
    return {"status": "ok"}
