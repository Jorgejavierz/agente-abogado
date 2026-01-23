from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"mensaje": "Hola desde FastAPI ✅"}

@app.get("/health")
async def health():
    return {"status": "ok"}