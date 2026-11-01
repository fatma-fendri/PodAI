from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import APIError, RateLimitError
from app.rag import search
from app.agent import agent_answer
from app.limits import DailyLimiter, client_ip
import logging
import os

logger = logging.getLogger("podai")

VISITOR_LIMIT_MESSAGE = (
    "You have reached the daily limit of questions for this demo. Please come back tomorrow."
)
TOTAL_LIMIT_MESSAGE = (
    "The demo has reached its daily capacity. Please try again tomorrow."
)
QUOTA_MESSAGE = (
    "The demo has used up its free daily capacity with the language model. Please try again later."
)

# Limits are set with environment variables. 0 (the default) means "no limit".
limiter = DailyLimiter(
    per_visitor=int(os.getenv("PODAI_LIMIT_PER_VISITOR", "0")),
    total=int(os.getenv("PODAI_LIMIT_TOTAL", "0")),
)

class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

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
def ask_endpoint(body: AskRequest, request: Request):
    reason = limiter.check(client_ip(request))
    if reason == "total":
        raise HTTPException(status_code=429, detail=TOTAL_LIMIT_MESSAGE)
    if reason == "visitor":
        raise HTTPException(status_code=429, detail=VISITOR_LIMIT_MESSAGE)
    try:
        return agent_answer(body.question)
    except RateLimitError as e:
        logger.warning("Groq quota reached")
        raise HTTPException(status_code=503, detail=QUOTA_MESSAGE) from e
    except APIError as e:
        logger.exception("Agent call failed")
        raise HTTPException(
            status_code=503,
            detail="The assistant is temporarily unavailable. Please try again.",
        ) from e