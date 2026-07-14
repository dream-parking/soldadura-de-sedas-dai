"""app/entrypoints/errors.py"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.service_layer.exceptions import (
    NotFoundError,
    WorkerNotAssignedToProject,
    QuoteNotApproved,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Traduce las excepciones del dominio y del service layer a respuestas HTTP."""

    @app.exception_handler(NotFoundError)
    async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(WorkerNotAssignedToProject)
    async def handle_conflict(request: Request, exc: WorkerNotAssignedToProject) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(QuoteNotApproved)
    async def handle_quote_not_approved(request: Request, exc: QuoteNotApproved) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def handle_invariant_violation(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})