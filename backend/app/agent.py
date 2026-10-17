import os
import re
import json
from dotenv import load_dotenv
from groq import Groq
from app.rag import search
from app.web_search import web_search

load_dotenv(override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-20b"
MAX_STEPS = 4
MAX_DISTANCE = 1.3

AGENT_PROMPT = """You are PodAI, an educational assistant about foot conditions.

Tools:
- search_knowledge_base: PodAI's verified knowledge base. Always try it first for any foot-related question.
- search_web: trusted medical websites. Use it only if the knowledge base has no relevant information, or if the question is about recent information.

Rules:
1. Scope: you only answer questions about foot and ankle conditions and foot health. For any other topic (cooking, general medicine, etc.), reply that this is outside your scope and do not call any tool.
2. After each piece of information, cite its source number in plain square brackets, for example [1] or [2].
3. If no tool returns relevant information, say that you do not have this information in your knowledge base. Never say "the sources you provided".
4. Never give a diagnosis. Remind the user that this information is educational and that a healthcare professional should be consulted.
5. Write the whole answer in the language of the user's question. If the question is in English, answer in English. Never switch languages.
6. Be concise: a few sentences.
7. Always write your search queries in English, even if the user's question is in another language, because the knowledge base and the trusted websites are in English. Then write your final answer in the user's language.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search PodAI's verified podiatry knowledge base. Use first for any foot-related question.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query, always written in English"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search trusted medical websites for foot and ankle health questions only. Use only if the knowledge base has no relevant information, or for recent information.",            
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query"}},
                "required": ["query"],
            },
        },
    },
]

def to_english(text):
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Translate the user's text to English. If it is already in English, return it unchanged. Output only the translation.",
            },
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()

def search_knowledge_base(query, sources):
    english_query = to_english(query)
    hits = [h for h in search(english_query) if h["distance"] <= MAX_DISTANCE]
    if not hits:
        return "No relevant document found in the knowledge base."
    parts = []
    for hit in hits:
        sources.append({"title": hit["title"], "url": hit["source_url"]})
        n = len(sources)
        parts.append(f"[{n}] {hit['title']}\n{hit['document']}")
    return "\n\n".join(parts)


def search_web(query, sources):
    results = web_search(query)
    if not results:
        return "No result found on trusted websites."
    parts = []
    for r in results:
        sources.append({"title": r["title"], "url": r["url"]})
        n = len(sources)
        parts.append(f"[{n}] {r['title']}\n{r['content']}")
    return "\n\n".join(parts)

def run_tool(name, args, sources):
    if name == "search_knowledge_base":
        return search_knowledge_base(args["query"], sources)
    if name == "search_web":
        return search_web(args["query"], sources)
    return "Unknown tool."

def agent_answer(question):
    sources = []
    messages = [
        {"role": "system", "content": AGENT_PROMPT},
        {"role": "user", "content": f"{question}\n\n(Answer in the same language as this question.)"},    
        ]
    for step in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto" if step < MAX_STEPS - 1 else "none",
        )
        message = response.choices[0].message
        if not message.tool_calls:
            break
        messages.append(message)
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            result = run_tool(call.function.name, args, sources)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    answer = message.content or "I could not complete the search."
    answer = re.sub(r"【(\d+)】", r"[\1]", answer)
    answer = answer.replace("\u202f", " ")
    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)})

    final_sources = []
    for i in cited:
        if 1 <= i <= len(sources):
            final_sources.append(sources[i - 1])

    return {"answer": answer, "sources": final_sources}


if __name__ == "__main__":
    for q in [
        "douleur au talon le matin",
    ]:
        print(q)
        print(agent_answer(q))
        print()