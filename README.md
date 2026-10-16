# PodAI

**A clinical podiatry assistant that answers from verified sources and cites them.**

PodAI combines a curated knowledge base (RAG) with web search (planned) so that every answer about foot conditions is grounded in identified sources, instead of relying on a language model's memory alone.

> **Status: work in progress.** This is a personal portfolio and learning project, built step by step. See [Roadmap](#roadmap) for what works today.

> **Disclaimer:** PodAI is for educational and demonstration purposes only. It does not provide medical advice, diagnosis or treatment and does not replace a healthcare professional. No real health data is collected or stored.

## Why

General-purpose chatbots can hallucinate medical information and rarely cite verifiable sources. PodAI addresses this reliability problem: the model is only allowed to answer from retrieved documents, and each answer points back to its source.

## Architecture

```
User ──► Next.js frontend ──► FastAPI backend ──► ChromaDB (knowledge base)
                                    │
                                    └──► Groq LLM (grounded answers with citations)
                                    └──► Tavily web search (planned)
```

Current request flow for `POST /ask`:

1. The client sends a question.
2. The backend retrieves the 3 closest documents from ChromaDB.
3. Documents beyond a distance threshold are discarded. If none remain, the API answers that it has no information, without calling the LLM.
4. The remaining documents are passed to the Groq LLM as numbered sources, with instructions to answer only from them and to cite them.
5. The API returns the answer and only the sources the model actually cited.

`POST /search` returns the raw retrieved documents and is kept for debugging.

## Tech stack

| Area | Tools |
| --- | --- |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Knowledge base | ChromaDB, default embedding model `all-MiniLM-L6-v2` |
| LLM | Groq API  |
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS |
| Planned | LangChain agent with tool-calling, Tavily, Docker, GitHub Actions CI/CD, Vercel and Render/Fly.io deployment |

## Project structure

```
PodAI/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app and routes
│   │   ├── rag.py         # ingestion and semantic search
│   │   └── llm.py         # Groq client (grounded answer generation)
│   ├── data/
│   │   └── podiatry_dataset.json   # 15 conditions
│   ├── .env.example
│   └── requirements.txt
├── frontend/              # Next.js app
├── docs/
└── README.md
```

## Getting started

Prerequisites: Python 3.13.2, Node.js v22.21.0, Git.

### Backend

From the `backend/` folder:

```bash
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file from the template and add your own Groq API key:

```bash
cp .env.example .env
# then edit .env and set GROQ_API_KEY
```

Build the knowledge base once (the first run downloads the embedding model):

```bash
python app/rag.py
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The interactive API documentation is available at `http://localhost:8000/docs`.

### Frontend

From the `frontend/` folder:

```bash
npm install
cp .env.example .env.local
npm run dev
```

The app runs on `http://localhost:3000`. `NEXT_PUBLIC_API_URL` in `.env.local` must point to the backend (default `http://localhost:8000`).

## API

| Method | Route | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/echo` | Echo test used to validate the frontend/backend connection |
| POST | `/search` | Semantic search over the knowledge base, returns the 3 closest documents |
| POST | `/ask` | Grounded answer from the knowledge base, with cited sources |

Example:

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"question": "pain in the heel when I wake up"}'
```

## Knowledge base

The current dataset contains 15 foot conditions (plantar fasciitis, hallux valgus, Achilles tendinopathy, Sever disease, tarsal tunnel syndrome and others), each with overview, symptoms, causes, diagnosis, treatment and a source reference.

The content is written in English and rephrased from public medical references. **Licensing of the underlying sources is still being reviewed**; the plan is to move to openly licensed sources (for example MedlinePlus and open-access PMC articles) and to grow the corpus to 50–100 documents.

## Early evaluation

A first manual check with 4 questions shows the current retrieval is promising but not yet reliable:

| Question | Expected | Result |
| --- | --- | --- |
| pain in the heel when I wake up | plantar fasciitis | rank 1 |
| my big toe is bending sideways | hallux valgus | rank 2 |
| numbness between my toes | plantar nerve compression | not in top 3 |
| how to bake bread (out of scope) | no answer | still returns 3 documents |

These cases are the seed of a 30-question evaluation set.

## Known limitations

- The default embedding model is English-oriented, while the goal is FR/EN/DE support.
- One document per condition may dilute meaning; section-level chunking is planned.
- No relevance threshold yet: out-of-scope questions still return documents.
- Small corpus (15 documents).

## Roadmap

- [x] Project setup, Git, FastAPI and Next.js skeletons
- [x] Frontend/backend integration (CORS, environment variables)
- [x] Knowledge base ingestion into ChromaDB
- [x] Semantic search endpoint (`POST /search`)
- [x] LLM answer generation grounded in retrieved sources, with citations
- [ ] Agent with tool-calling (knowledge base vs. Tavily web search)
- [ ] Chat interface with sources and medical disclaimer
- [ ] Evaluation set and metrics (hit@k, precision@k, RAGAS)
- [ ] Retrieval improvements: multilingual embeddings, hybrid search (BM25), reranking
- [ ] Docker, CI/CD, deployment
- [ ] V2: MCP servers for tools, PostgreSQL history and feedback, Arabic with RTL support

## Author

Fatma Fendri — AI engineer based in Munich.