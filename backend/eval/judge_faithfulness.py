import json

from app.rag import build_document
from app.agent import MODEL, get_client


with open("data/podiatry_dataset.json", encoding="utf-8") as f:
    DATASET = json.load(f)


def source_text(url):
    for fiche in DATASET:
        if fiche["source"]["url"] == url:
            return build_document(fiche)
    return None

JUDGE_PROMPT = """You check whether an answer is supported by source documents.

You receive SOURCES and an ANSWER. Split the ANSWER into its factual sentences
and give each one a label:
- OK: the sources say it clearly.
- PARTIAL: the sources say something close, but the sentence adds a detail
  that they do not contain.
- NO: the sentence is absent from the sources, or contradicted by them.

Rules:
- Judge only against the SOURCES, never against your own knowledge, even if
  the sentence is true.
- Skip sentences that make no medical claim, such as "consult a healthcare
  professional".
- Reply with JSON only: a list with one object per sentence, each object
  having the keys "sentence", "label" (OK, PARTIAL or NO) and "reason"
  (one short line).
- Check every detail of a sentence: timing, names of exercises, numbers,
  causes and mechanisms. If the main idea is in the sources but a detail of
  the sentence is not in the sources, label the sentence PARTIAL, not OK.
- If a sentence gives a cause or a mechanism that the sources attribute to
  something else, or do not give, label it NO.

SOURCES:
{sources}

ANSWER:
{answer}
"""

def judge(answer, urls):
    texts = [source_text(u) for u in urls]
    sources = "\n\n".join(
        f"[{i}] {t}" for i, t in enumerate(texts, start=1) if t
    )
    prompt = JUDGE_PROMPT.format(sources=sources, answer=answer)
    response = get_client().chat.completions.create(
        model=MODEL,
        temperature=0,
        seed=0,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    return json.loads(content)