"""app/entrypoints/routers/__init__.py

Router principal de la API: agrega los routers de cada recurso.
Los endpoints CRUD de cada entidad (Épica 2) se registran aquí conforme se implementen.
"""
from fastapi import APIRouter

from app.entrypoints.routers.clients import router as clients_router
from app.entrypoints.routers.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(clients_router)
