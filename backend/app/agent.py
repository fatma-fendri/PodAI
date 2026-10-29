import os
import re
import json
from dotenv import load_dotenv
from groq import Groq
from app.rag import search, rerank
from app.web_search import web_search
from groq import BadRequestError
from langdetect import detect, DetectorFactory


load_dotenv(override=True)
_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"), max_retries=5)
    return _client
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
11. Only mention treatments, exercises and self-care measures that appear in the
    documents or search results you received. Do not add advice from your own
    knowledge, even if it is common medical advice or seems obvious. You may still tell the person to see a healthcare
    professional.
12. EXCEPTION to rules 2, 8 and 11: if the user describes a possible
    medical emergency, do not call any tool. Answer immediately in the
    user's language with a short message: this may be urgent, they should
    seek medical care now or call their local emergency number, and they
    should not wait or try home treatment. Do not name a diagnosis and do
    not give self-care advice. Possible emergencies: a foot that is
    suddenly cold, pale or blue with severe pain or numbness; a wound on
    a diabetic foot with spreading redness, pus, a bad smell or fever;
    swelling and pain in one calf, especially with shortness of breath or
    chest pain; a hot, red, swollen joint together with fever. A
    persistent problem without these signs is not an emergency: answer
    normally.
"""

CLINICAL_PROMPT = """
You rewrite a patient's foot-problem description as a search query for a podiatry knowledge base.

Output the original text, followed by the anatomical and clinical terms that correspond to the patient's everyday words.
Examples of the mapping:
- "top of the foot" -> dorsum of the foot
- "outer side of the ankle" -> lateral malleolus
- "outer edge of the foot" -> lateral border of the foot, fifth metatarsal
- "bottom of the foot" -> plantar surface

Rules:
- Keep all the patient's original words.
- Add only anatomical locations and clinical descriptions of the symptoms (for example swelling, joint stiffness, pain on push-off).
- Do NOT name any disease, condition or diagnosis.
- Output only the query text, on a single line, with no introduction and no explanation.
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

FALLBACKS = {
    "English": "I could not find reliable information about this in my sources. Please consult a healthcare professional.",
    "French": "Je n’ai pas trouvé d’information fiable à ce sujet dans mes sources. Veuillez consulter un professionnel de santé.",
    "German": "Ich konnte dazu keine verlässlichen Informationen in meinen Quellen finden. Bitte konsultieren Sie medizinisches Fachpersonal.",
}


def to_english(text):
    response = get_client().chat.completions.create(
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

def to_clinical(text):
    try:
        response = get_client().chat.completions.create(
            model=MODEL,
            temperature=0,
            seed=0,
            messages=[
                {"role": "system", "content": CLINICAL_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        return (response.choices[0].message.content or "").strip()
    except Exception:
        return ""

def add_source(sources, title, url, origin):
    for i, s in enumerate(sources, start=1):
        if normalize_url(s["url"]) == normalize_url(url):
            return i
    sources.append({"title": title, "url": url, "origin": origin})
    return len(sources)

def search_knowledge_base(query, sources):
    english_query = to_english(query)
    clinical = to_clinical(english_query)
    kb_query = english_query + " " + clinical if clinical else english_query
    if os.getenv("PODAI_RERANK") == "1":
        candidates = [h for h in search(kb_query, n_results=10) if h["distance"] <= MAX_DISTANCE]
        hits = rerank(english_query, candidates, 5)
    else:
        hits = [h for h in search(kb_query, n_results=5) if h["distance"] <= MAX_DISTANCE]
    if not hits: 
        return "No relevant document found in the knowledge base."
    parts = []
    for hit in hits:
        n = add_source(sources, hit["title"], hit["source_url"], "Knowledge base")
        parts.append(f"[{n}] {hit['title']}\n{hit['document']}")
    return "\n\n".join(parts)


def search_web(query, sources):
    results = web_search(to_english(query))
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


def fallback_message(language):
    return FALLBACKS.get(language, FALLBACKS["English"])


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
            response = get_client().chat.completions.create(**kwargs)
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
        retry = get_client().chat.completions.create(model=MODEL, temperature=0, seed=0, messages=messages)
        answer, final_sources = finalize(retry.choices[0].message.content or answer, sources)

        if not final_sources:
            answer = fallback_message(language)

    return {"answer": answer, "sources": final_sources, "trace": trace}
    

if __name__ == "__main__":
    for q in [
        "I am a teenager with pain and swelling at the base of my second toe that started after sports, and the joint feels stiff.",
    ]:
        print(q)
        print(agent_answer(q))
        print()