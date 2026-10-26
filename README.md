# PodAI

![tests](https://github.com/fatma-fendri/PodAI/actions/workflows/tests.yml/badge.svg)

**A clinical podiatry assistant that answers from verified sources and cites them.**

PodAI combines a curated knowledge base (RAG) with web search restricted to trusted medical domains, so that every answer about foot conditions is grounded in identified sources, instead of relying on a language model's memory alone.

> **Status: work in progress.** This is a personal portfolio and learning project, built step by step. See [Roadmap](#roadmap) for what works today.

> **Disclaimer:** PodAI is for educational and demonstration purposes only. It does not provide medical advice, diagnosis or treatment and does not replace a healthcare professional. No real health data is collected or stored.

## Why

General-purpose chatbots can hallucinate medical information and rarely cite verifiable sources. PodAI addresses this reliability problem: the model is asked to answer from retrieved documents, and each answer points back to its source.

## Architecture

```
User ──► Next.js frontend ──► FastAPI backend ──► ChromaDB (knowledge base)
                                    │
                                    └──► Groq LLM (agent with tool-calling, grounded answers with citations)
                                    └──► Tavily web search (trusted medical domains only)
```

Current request flow for `POST /ask`:

1. The client sends a question, in any language.
2. An agent (Groq LLM with tool-calling) decides which tool to use:
   - `search_knowledge_base`: the query is translated to English, then ChromaDB returns the 5 closest documents. Documents beyond a distance threshold are discarded.
   - `search_web`: Tavily search restricted to trusted medical domains (MedlinePlus, NHS, NCBI, Mayo Clinic), used only when the knowledge base has no relevant information. Web queries are also translated to English.
3. Questions outside foot and ankle health are refused without calling any tool.
4. The answer is written in the user's language, with numbered citations.
5. A citation guard checks that the answer cites at least one retrieved source. If not, the model is asked once to rewrite using only the sources; if it still cites nothing, a safe fallback message is returned instead of an unsourced answer.
6. The API returns the answer, the sources the model actually cited (renumbered 1..n, deduplicated, and labelled "Knowledge base" or "Trusted Websites"), and a trace of the tool calls.

`POST /search` returns the raw retrieved documents and is kept for debugging.

## Tech stack

| Area | Tools |
| --- | --- |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Knowledge base | ChromaDB, default embedding model `all-MiniLM-L6-v2` |
| LLM | Groq API (`openai/gpt-oss-20b`) |
| Web search | Tavily, restricted to trusted domains |
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS, react-markdown |
| Tests | pytest, GitHub Actions |
| Planned | LangGraph (agent comparison), Docker, Vercel and Render/Fly.io deployment |

## Project structure

```
PodAI/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app and routes
│   │   ├── rag.py         # ingestion and semantic search
│   │   ├── llm.py         # RAG-only answers (baseline for evaluation)
│   │   ├── agent.py       # tool-calling agent, citation guard, source handling
│   │   └── web_search.py  # Tavily search limited to trusted domains
│   ├── data/
│   │   ├── podiatry_dataset.json   # 15 conditions
│   │   └── search_hints.json       # patient-wording phrases per condition (experiment)
│   ├── eval/
│   │   ├── questions.json          # 36 evaluation questions
│   │   ├── run_retrieval.py        # retrieval-only evaluation (hit@3, no LLM cost)
│   │   ├── rank_check.py           # rank of the expected condition among all 15
│   │   ├── run_eval.py             # full agent evaluation (resumable)
│   │   ├── run_subset.py           # replay a few questions
│   │   ├── score_eval.py           # automatic scoring of agent answers
│   │   ├── build_multi.py          # multilingual embeddings experiment
│   │   └── build_enriched.py       # enriched documents experiment
│   ├── tests/                      # pytest tests (citations, fallback)
│   ├── pytest.ini
│   ├── .env.example
│   └── requirements.txt
├── .github/workflows/     # CI: tests on every push
├── frontend/              # Next.js chat interface
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

Create a `.env` file from the template and add your own API keys (Groq and Tavily). Never commit this file.

```bash
cp .env.example .env
# then edit .env
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

Open `http://localhost:3000` (use `localhost`, not the "Network" address that Next.js also prints). `NEXT_PUBLIC_API_URL` in `.env.local` must point to the backend (default `http://localhost:8000`). Variables starting with `NEXT_PUBLIC_` are visible in the browser, so no secret goes there.

### Tests

From the `backend/` folder (no API key needed):

```bash
pytest
```

The same tests run on every push with GitHub Actions.

## API

| Method | Route | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/echo` | Echo test used to validate the frontend/backend connection |
| POST | `/search` | Semantic search over the knowledge base, returns the 3 closest documents |
| POST | `/ask` | Agent answer with cited sources and a tool-call trace |

Example:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "pain in the heel when I wake up"}'
```

The response contains `answer`, `sources` (each with `title`, `url` and `origin`) and `trace`. If the language model API is unavailable, the endpoint returns a 503 with a generic message and logs the cause.

## Knowledge base

The current dataset contains 15 foot conditions (plantar fasciitis, hallux valgus, Achilles tendinopathy, Sever disease, tarsal tunnel syndrome and others), each with overview, symptoms, causes, diagnosis, treatment and a source reference.

The content is written in English and rephrased from public medical references. **Licensing of the underlying sources is still being reviewed**; the plan is to move to openly licensed sources (for example MedlinePlus and open-access PMC articles) and to grow the corpus to 50–100 documents.

## Evaluation

The evaluation set (`backend/eval/questions.json`) has 36 questions: 16 in the knowledge base (English), 6 not in the knowledge base (web search expected), 4 out of scope, 3 safety (diagnosis request, medication dose, prompt injection) and 7 multilingual (French and German). 21 of them have an expected condition and are scored by retrieval, using hit@3 (the expected condition appears in the 3 retrieved documents). This costs no LLM call:

```bash
cd backend
python -m eval.run_retrieval base
python -m eval.run_retrieval enriched
```

| Experiment | 15 development questions | 6 held-out questions |
| --- | --- | --- |
| Baseline (`all-MiniLM-L6-v2`, one document per condition) | 12/15 | 4/6 |
| Multilingual embeddings (`paraphrase-multilingual-MiniLM-L12-v2`), original questions | 9/15 | not run |
| Multilingual embeddings, questions translated to English | 12/15 | not run |
| Documents enriched with patient-wording phrases | 14/15 | 4/6 |

What I learned:

- The multilingual model did not help once questions are translated to English, so the default model is kept.
- Enriching the documents fixed two development misses, but those phrases were written after seeing the failures. On six questions written afterwards, nothing changed, so the gain is **not proven to generalize**. One question moves hit@3 by about 5 points, so these differences are within noise.
- Misses are mostly a vocabulary gap between patient wording and clinical text (for example Freiberg disease), and embeddings ignore negation ("no tingling or numbness").
- Distances cannot separate "not in the knowledge base" from "present", so a relevance threshold alone is not enough.
- Some labels were adjusted after the first retrieval runs (documented in the `notes` field of `questions.json`), which is a known risk of tuning a test set.

### Full agent evaluation

`python -m eval.run_eval` runs the whole agent on the 36 questions and `python -m eval.score_eval` scores each answer. A question is **PASS** when the right source is cited, the refusal or safety rule is respected and the answer is in the user's language. PASS does **not** mean every sentence is supported by the sources.

| Run | Main change | Score | Failed questions |
| --- | --- | --- | --- |
| v3 | Baseline agent, 3 documents per search | 31/36 | q04, q05, q09, q26, q31 |
| v4 | Answer language enforced, no medication advice for children | 31/36 | q04, q09, q11, q26, q31 |
| v5 | 5 documents per search instead of 3 | 31/36 | q09, q11, q14, q30, q31 |

What I learned:

- A rank check of the expected condition among all 15 showed that several misses were close: hit@3 is 16/21 and hit@5 is 19/21. Only Freiberg disease stays out of reach (rank 7 and 15). Part of this gain comes from the small corpus, since 5 documents out of 15 is a third of the base, and I chose k=5 after seeing the ranks, so the gain may not carry over to a larger corpus.
- The score stayed at 31/36 in all three runs, but the failed questions changed each time. With one question worth about 3 points on 36, a difference of one or two questions is within noise, so these runs show no real improvement.
- Question q14 shows a limit of the citation guard: the agent states facts that are not in the retrieved documents and still cites them. With more documents returned, it also answered from the knowledge base instead of searching the web. The scorer cannot see this, which is why a faithfulness measure comes next.
- Changes made after v5 (web queries translated to English, answers in the user's language when the fallback message is used) are tested on single questions but not yet in a full run.

## Known limitations

- Retrieval still misses some conditions whose clinical wording differs from patient language: hit@3 16/21, hit@5 19/21 on the scored questions. Freiberg disease stays out of reach (rank 7 and 15 of 15). Part of the hit@5 gain comes from the small corpus: 5 documents out of 15 is a third of the base.
- Embeddings ignore negation.
- The citation guard checks that a source is cited, not that it supports each claim. In question q14 the agent states facts that are not in the retrieved documents and cites them anyway. Answer faithfulness is not measured yet.
- Answers are not fully deterministic, even at temperature 0, because of the model and live web search.
- The agent does not always pick the right tool: with 5 documents returned, it can answer from the knowledge base when the question is not covered, instead of going to the web.
- No relevance threshold: out-of-scope questions still return documents from the knowledge base (they are filtered by the agent, not by retrieval).
- Small corpus (15 documents); licensing of the underlying sources is still being reviewed.
- The scope is strict (foot and ankle): related topics such as knee pain are refused.
- The agent costs 2 to 4 LLM calls per question and depends on a free-tier quota.

## Roadmap

- [x] Project setup, Git, FastAPI and Next.js skeletons
- [x] Frontend/backend integration (CORS, environment variables)
- [x] Knowledge base ingestion into ChromaDB
- [x] Semantic search endpoint (`POST /search`)
- [x] LLM answer generation grounded in retrieved sources, with citations
- [x] Agent with tool-calling (knowledge base vs. Tavily web search)
- [x] Chat interface with sources and medical disclaimer
- [x] Evaluation set (36 questions) and retrieval metrics (hit@3)
- [x] Full agent evaluation: 36 questions, automatic scorer (31/36 PASS)
- [ ] Answer faithfulness measure (LLM judge or RAGAS)
- [ ] Retrieval improvements: hybrid search (BM25), reranking, query rewriting (section-level chunking was ruled out: documents are only 91 to 168 words)
- [x] Tests and CI (pytest, GitHub Actions)
- [ ] Docker and deployment
- [ ] V2: MCP servers for tools, PostgreSQL history and feedback, Arabic with RTL support

## Author

Fatma Fendri — AI engineer based in Munich.