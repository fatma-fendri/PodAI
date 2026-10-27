import json
import sys
import time

from eval.judge_faithfulness import judge

RESULTS = sys.argv[1]
OUTPUT = sys.argv[2]

with open(RESULTS, encoding="utf-8") as f:
    results = json.load(f)

out = {}
for r in results:
    sources = r["sources"]
    if not sources or any(s["origin"] != "Knowledge base" for s in sources):
        continue
    urls = [s["url"] for s in sources]
    try:
        out[r["id"]] = judge(r["answer"], urls)
    except Exception as e:
        out[r["id"]] = {"error": str(e)}
        print(r["id"], "ERROR")
        continue
    print(r["id"], "done")
    time.sleep(10)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)