FROM python:3.13-slim

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY app ./app
COPY data ./data

# Build the knowledge base and download the models once, at build time
RUN python -c "from app.rag import ingest; ingest()" \
 && python -c "from flashrank import Ranker; Ranker(model_name='ms-marco-MiniLM-L-12-v2')"

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]