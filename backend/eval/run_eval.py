import json
import sys
import time
from pathlib import Path

from app.agent import agent_answer

QUESTIONS_PATH = Path("eval/questions.json")
RESULTS_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("eval/results_agent_v3.json")


def run():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    results = []

    results = []
    if RESULTS_PATH.exists():
        results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        results = [r for r in results if not r["error"]]
    done = {r["id"] for r in results}

    for q in questions:
        if q["id"] in done:
            continue
        print(f"{q['id']} ...")
        start = time.time()
        try:
            output = agent_answer(q["question"])      
            error = None
        except Exception as e:
            output = {"answer": "", "sources": [], "trace": []}
            error = str(e)
        duration = round(time.time() - start, 1)

        if error and "429" in error:
            print("Rate limit reached, stopping. Run the same command later to resume.")
            break

        results.append({
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "answer": output["answer"],
            "sources": output["sources"],
            "trace": output["trace"],
            "error": error,
            "duration_s": duration,
        })
        RESULTS_PATH.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        time.sleep(2)

    print(f"Done: {len(results)} results in {RESULTS_PATH}")


if __name__ == "__main__":
    run()