#!/usr/bin/env python3
"""
Servidor de prueba simple
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Servidor de prueba funcionando"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Servidor funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001) 