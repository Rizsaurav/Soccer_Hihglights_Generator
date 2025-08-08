from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.fastAPI.routes import upload  # updated import path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev, limit this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)

@app.get("/")
def root():
    return {"message": "FastAPI backend running from root"}
