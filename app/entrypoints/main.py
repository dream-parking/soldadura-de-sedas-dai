from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_allowed_origins
from app.entrypoints.errors import register_exception_handlers
from app.entrypoints.routers import api_router

app = FastAPI(title="Soldadura de Sedas API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Soldadura de Sedas API OK"}
