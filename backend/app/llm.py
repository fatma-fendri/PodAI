import os
import re
from dotenv import load_dotenv
from groq import Groq
from app.rag import search

load_dotenv(override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"
MAX_DISTANCE = 1.3

SYSTEM_PROMPT = """You are PodAI, an educational assistant that provides information about foot conditions.

Rules:
1. Answer ONLY using the numbered sources provided below the user's question. These sources come from PodAI's own knowledge base, not from the user. Do not use any outside knowledge.
2. After each piece of information, cite the source number in square brackets, for example [1] or [2] and use plain square brackets such as [1], never other bracket styles.
3. If the sources do not contain the answer, say that you do not have this information in your knowledge base. Never say "the sources you provided" or refer to the user as the source of the information. Do not guess and do not invent anything.
4. Never give a diagnosis. Remind the user that this information is educational and that a healthcare professional should be consulted for any medical concern.
5. Reply in the same language as the user's question.
6. Be concise: a short, clear answer in a few sentences.
"""


def ask_llm(question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content

def build_context(hits):
    parts = []
    for i, hit in enumerate(hits, start=1):
        parts.append(f"[{i}] {hit['title']}\n{hit['document']}")
    return "\n\n".join(parts)

def answer_question(question):
    hits = search(question)
    hits = [h for h in hits if h["distance"] <= MAX_DISTANCE]
    if not hits:
        return {
            "answer": "I do not have this information in my knowledge base.",
            "sources": [],
        }
    context = build_context(hits)
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {question}"},
        ],
    )
    answer = response.choices[0].message.content
    answer = re.sub(r"【(\d+)】", r"[\1]", answer)
    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)})

    sources = []
    for i in cited:
        if 1 <= i <= len(hits):
            hit = hits[i - 1]
            sources.append({"title": hit["title"], "url": hit["source_url"]})

    return {
        "answer": answer,
        "sources": sources,
    }
    

if __name__ == "__main__":
    #print(ask_llm("In one sentence, what is plantar fasciitis?"))
    for q in [
        "pain in the heel when I wake up",
        "how to bake bread",
        "knee pain after running"
    ]:
        print(q)
        print(answer_question(q))   
        print()