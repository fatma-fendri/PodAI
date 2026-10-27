import json

from app.rag import build_document
from app.agent import get_client


with open("data/podiatry_dataset.json", encoding="utf-8") as f:
    DATASET = json.load(f)


def source_text(url):
    for fiche in DATASET:
        if fiche["source"]["url"] == url:
            return build_document(fiche)
    return None

JUDGE_MODEL = "openai/gpt-oss-120b"

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
- Skip a sentence only if it contains no factual claim at all, such as
  "consult a doctor", "see a podiatrist" or "ask a pharmacist". Never skip a
  sentence that names a treatment, a cause or a symptom, even when it also
  advises seeing a professional.
- If a sentence lists several items (treatments, causes, symptoms), judge it
  by its weakest items: if one listed item is not in the sources, the label is
  PARTIAL at best, and NO if most of the listed items are not in the sources.
- Do not label a sentence PARTIAL only because it uses a different word for
  the same thing (for example "puffiness" and "swelling"). PARTIAL needs a
  fact, a number, a time or a cause that is missing from the sources.
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
    for attempt in range(2):
        response = get_client().chat.completions.create(
            model=JUDGE_MODEL,
            temperature=0,
            seed=0,
            max_completion_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content or ""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            continue
    raise ValueError("judge returned invalid JSON twice")