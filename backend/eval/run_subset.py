import json
import sys
import time

from app.agent import agent_answer

QUESTIONS_PATH = "eval/questions.json"


def main(output_path, ids):
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        questions = [q for q in json.load(f) if q["id"] in ids]

    results = []
    for q in questions:
        try:
            out = agent_answer(q["question"])
            results.append({"id": q["id"], "answer": out["answer"],
                            "sources": out["sources"], "trace": out["trace"],
                            "error": None})
        except Exception as e:
            results.append({"id": q["id"], "answer": "", "sources": [],
                            "trace": [], "error": str(e)})
        print(q["id"], "done")
        time.sleep(2)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])