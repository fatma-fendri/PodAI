from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.rag import search

class EchoRequest(BaseModel):
    message: str
   
class SearchRequest(BaseModel):
    question: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
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