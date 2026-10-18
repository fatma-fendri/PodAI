import json
import time
from pathlib import Path

from app.agent import agent_answer

QUESTIONS_PATH = Path("eval/questions.json")
RESULTS_PATH = Path("eval/results_agent.json")


def run():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    results = []

    for q in questions:
        print(f"{q['id']} ...")
        start = time.time()
        try:
            output = agent_answer(q["question"])      
            error = None
        except Exception as e:
            output = {"answer": "", "sources": [], "trace": []}
            error = str(e)
        duration = round(time.time() - start, 1)

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
        time.sleep(2)   

    RESULTS_PATH.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Done: {len(results)} results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    run()