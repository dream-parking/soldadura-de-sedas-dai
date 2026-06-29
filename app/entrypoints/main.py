from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Soldadura de Sedas API OK"}