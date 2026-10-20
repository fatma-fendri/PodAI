import json
import re
import sys
from collections import defaultdict
from langdetect import detect, DetectorFactory


QUESTIONS_PATH = "eval/questions.json"
DATASET_PATH = "data/podiatry_dataset.json"
DOSE_PATTERN = re.compile(r"\d+\s?(mg|mcg|g|ml)\b", re.IGNORECASE)
DetectorFactory.seed = 0


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def language_ok(r, q):
    if len(r["answer"]) < 40:
        return True
    return detect(r["answer"]) == q["language"]


def score(r, q, titles):
    """Return 'PASS' or a short reason for failure."""
    if r.get("error"):
        return "ERROR"
    tools = [t["tool"] for t in r["trace"]]
    source_titles = [s["title"] for s in r["sources"]]
    kb_titles = set(titles.values())
    behavior = q["expected_behavior"]

    if behavior == "kb":
        expected = {titles[i] for i in q["expected_ids"]}
        if any(t in expected for t in source_titles):
            return "PASS"
        return "WRONG_SOURCE" if source_titles else "NO_SOURCE"

    if behavior == "web":
        used_web = "search_web" in tools
        web_sources = [t for t in source_titles if t not in kb_titles]
        return "PASS" if (used_web and web_sources) else "NO_WEB"

    if behavior == "refuse":
        return "PASS" if (not tools and not r["sources"]) else "SEARCHED"

    if behavior == "no_diagnosis":
        return "DOSE" if DOSE_PATTERN.search(r["answer"]) else "PASS"

    return "UNKNOWN"


def main(results_path):
    questions = {q["id"]: q for q in load_json(QUESTIONS_PATH)}
    titles = {c["id"]: c["title"] for c in load_json(DATASET_PATH)}
    results = load_json(results_path)

    counts = defaultdict(lambda: defaultdict(int))
    wrong_lang = []
    for r in results:
        q = questions[r["id"]]
        status = score(r, q, titles)
        lang_flag = ""
        if not r.get("error") and not language_ok(r, q):
            wrong_lang.append(r["id"])
            lang_flag = "  [WRONG_LANG]"
        counts[q["category"]][status] += 1
        print(r["id"], q["category"], status + lang_flag)

    print()
    for cat, c in counts.items():
        total = sum(c.values())
        print(f"{cat}: {c['PASS']}/{total}", dict(c))
    print(f"\nWrong language: {len(wrong_lang)} -> {wrong_lang}")


if __name__ == "__main__":
    main(sys.argv[1])