from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import APIError
from app.rag import search
from app.agent import agent_answer
import logging
import os

logger = logging.getLogger("podai")

class AskRequest(BaseModel):
    question: str

class EchoRequest(BaseModel):
    message: str
   
class SearchRequest(BaseModel):
    question: str

app = FastAPI()
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}   

@app.post("/echo")
async def echo(request: EchoRequest):
    return {"message": request.message}

@app.post("/search")
def search_endpoint(request: SearchRequest):
    hits = search(request.question)
    return {"results": hits}

@app.post("/ask")
def ask_endpoint(request: AskRequest):
    try:
        return agent_answer(request.question)
    except APIError as e:
        logger.exception("Agent call failed")
        raise HTTPException(
            status_code=503,
            detail="The assistant is temporarily unavailable. Please try again.",
        ) from e