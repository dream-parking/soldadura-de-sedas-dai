from fastapi import FastAPI
from fastapi.exceptions import ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
 
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
 
 
@app.exception_handler(ResponseValidationError)
async def debug_response_validation_handler(request, exc):
    print("=" * 60)
    print("ERROR REAL DE VALIDACION DE RESPUESTA:")
    for err in exc.errors():
        print(err)
    print("=" * 60)
    return JSONResponse(status_code=500, content={"detail": "Error de validacion de respuesta (debug)"})
 
 
app.include_router(api_router, prefix="/api")
 
 
@app.get("/")
def root():
    return {"message": "Soldadura de Sedas API OK"}
 
