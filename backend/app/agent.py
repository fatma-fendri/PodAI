import os
import re
import json
from dotenv import load_dotenv
from groq import Groq
from app.rag import search
from app.web_search import web_search
from groq import BadRequestError
from langdetect import detect, DetectorFactory


load_dotenv(override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-20b"
MAX_STEPS = 4
MAX_DISTANCE = 1.3
DetectorFactory.seed = 0

LANGUAGE_NAMES = {"en": "English", "fr": "French", "de": "German"}


AGENT_PROMPT = """You are PodAI, an educational assistant about foot conditions.

Tools:
- search_knowledge_base: PodAI's verified knowledge base. Always try it first for any foot-related question.
- search_web: trusted medical websites. Use it only if the knowledge base has no relevant information, or if the question is about recent information.

Rules:
1. Scope: you only answer questions about foot and ankle conditions and foot health. For any other topic (cooking, general medicine, etc.), reply that this is outside your scope and do not call any tool.
2. After each sentence that uses information from a source, cite its number in plain square brackets, for example [1] or [2]. Put the citation at the end of that sentence, not only at the end of the answer.
3. If no tool returns relevant information, say that you do not have this information in your knowledge base. Never say "the sources you provided".
4. Never give a diagnosis. Remind the user that this information is educational and that a healthcare professional should be consulted.
5. Write the whole answer in the language of the user's question. If the question is in English, answer in English. Never switch languages.
6. Be concise: a few sentences.
7. Always write your search queries in English, even if the user's question is in another language, because the knowledge base and the trusted websites are in English. Then write your final answer in the user's language.
8. Use only facts that appear in the tool results. Do not add details from your own knowledge. If the tool results do not answer the question, say so.
9. Never give a medication dose, quantity or schedule. If asked for one, say that a pharmacist or a doctor must advise.
10. If the user is, or is asking about, a child or a teenager, do not mention any medication, including anti-inflammatories and pain relievers, even if a source does. Say that a doctor or a pharmacist must advise on this for children.
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
        seed=0,
        messages=[
            {
                "role": "system",
                "content": "Translate the user's text to English. If it is already in English, return it unchanged. Output only the translation.",
            },
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()


def normalize_url(url):
    return re.sub(r"^https?://", "", url).rstrip("/")


def add_source(sources, title, url, origin):
    for i, s in enumerate(sources, start=1):
        if normalize_url(s["url"]) == normalize_url(url):
            return i
    sources.append({"title": title, "url": url, "origin": origin})
    return len(sources)

def search_knowledge_base(query, sources):
    english_query = to_english(query)
    hits = [h for h in search(english_query) if h["distance"] <= MAX_DISTANCE]
    if not hits:
        return "No relevant document found in the knowledge base."
    parts = []
    for hit in hits:
        n = add_source(sources, hit["title"], hit["source_url"], "Knowledge base")
        parts.append(f"[{n}] {hit['title']}\n{hit['document']}")
    return "\n\n".join(parts)


def search_web(query, sources):
    results = web_search(query)
    if not results:
        return "No result found on trusted websites."
    parts = []
    for r in results:
        n = add_source(sources, r["title"], r["url"], "Trusted Websites")
        parts.append(f"[{n}] {r['title']}\n{r['content']}")
    return "\n\n".join(parts)

def run_tool(name, args, sources):
    if name == "search_knowledge_base":
        return search_knowledge_base(args["query"], sources)
    if name == "search_web":
        return search_web(args["query"], sources)
    return "Unknown tool."

def finalize(answer, sources):
    answer = re.sub(r"【(\d+)】", r"[\1]", answer)
    answer = answer.replace("\u202f", " ")
    def split_group(match):
        return "".join(f"[{n}]" for n in re.findall(r"\d+", match.group(1)))
    answer = re.sub(r"\[(\d+(?:\s*,\s*\d+)+)\]", split_group, answer)
    cited = []
    for m in re.findall(r"\[(\d+)\]", answer):
        n = int(m)
        if n not in cited and 1 <= n <= len(sources):
            cited.append(n)
    mapping = {old: new for new, old in enumerate(cited, start=1)}

    def renumber(match):
        old = int(match.group(1))
        return f"[{mapping[old]}]" if old in mapping else ""

    answer = re.sub(r"\[(\d+)\]", renumber, answer)
    return answer, [sources[old - 1] for old in cited]


def question_language(question):
    try:
        code = detect(question)
    except Exception:
        return "English"
    return LANGUAGE_NAMES.get(code, "English")


def agent_answer(question):
    sources = []
    trace = []
    language = question_language(question)
    messages = [
        {"role": "system", "content": AGENT_PROMPT},
        {"role": "user", "content": f"{question}\n\n(Write your final answer in {language}.)"},
    ]
    for step in range(MAX_STEPS):
        last = step == MAX_STEPS - 1
        kwargs = {"model": MODEL, "temperature": 0, "seed": 0, "messages": messages}
        if last:
            messages.append({
                "role": "user",
                "content": f"You cannot call any more tools. Write your final answer now in {language}, "
                           "using only the information already retrieved, and cite it as [n].",
            })
        else:
            kwargs["tools"] = TOOLS
            kwargs["tool_choice"] = "auto"
        try:
            response = client.chat.completions.create(**kwargs)
        except BadRequestError:
            if last:
                break
            raise
        message = response.choices[0].message
        if not message.tool_calls:
            break
        messages.append(message)
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            before = len(sources)
            result = run_tool(call.function.name, args, sources)
            trace.append({
                "tool": call.function.name,
                "query": args.get("query"),
                "results": len(sources) - before,
                "titles": [s["title"] for s in sources[before:]],
            })
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    answer = message.content or "I could not complete the search."
    answer, final_sources = finalize(answer, sources)
    if sources and not final_sources:
        messages.append({"role": "assistant", "content": answer})
        messages.append({
            "role": "user",
            "content": "Rewrite your answer using only the retrieved sources and cite them as [n]. "
                       "If they do not answer the question, say that you do not have this information.",
        })
        retry = client.chat.completions.create(model=MODEL, temperature=0, seed=0, messages=messages)
        answer, final_sources = finalize(retry.choices[0].message.content or answer, sources)

        if not final_sources:
            answer = ("I could not find reliable information about this in my sources. "
                      "Please consult a healthcare professional.")

    return {"answer": answer, "sources": final_sources, "trace": trace}
    

if __name__ == "__main__":
    for q in [
        "I am a teenager with pain and swelling at the base of my second toe that started after sports, and the joint feels stiff.",
    ]:
        print(q)
        print(agent_answer(q))
        print()