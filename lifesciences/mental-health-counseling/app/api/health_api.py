from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health", tags=['Health'])
def health_check():
    return JSONResponse(content={'status': 'ok'})