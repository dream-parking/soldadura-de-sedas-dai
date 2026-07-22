"""app/entrypoints/routers/__init__.py

Agrupa todos los routers de la API bajo un único api_router,
que main.py monta con el prefijo /api.
"""
from fastapi import APIRouter

from app.entrypoints.routers.clients import router as clients_router
from app.entrypoints.routers.health import router as health_router
from app.entrypoints.routers.quotes import router as quotes_router
from app.entrypoints.routers.projects import router as projects_router
from app.entrypoints.routers.workers import router as workers_router
from app.entrypoints.routers.account_statements import router as account_statements_router
from app.entrypoints.routers.biweekly_requests import router as biweekly_requests_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(clients_router)
api_router.include_router(quotes_router)
api_router.include_router(projects_router)
api_router.include_router(workers_router)
api_router.include_router(account_statements_router)
api_router.include_router(biweekly_requests_router)