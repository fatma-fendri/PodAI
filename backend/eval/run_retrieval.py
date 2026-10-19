import json
import sys
from pathlib import Path
from app.rag import search
from eval.build_multi import search_multi
from eval.build_enriched import search_enriched

MODE = sys.argv[1] if len(sys.argv) > 1 else "base"

QUESTIONS_PATH = Path("eval/questions.json")

ID_TO_TITLE = {
    "plantar_fasciitis": "Plantar Fasciitis",
    "hallux_valgus": "Bunion (Hallux Valgus)",
    "achilles_tendinopathy": "Achilles Tendinopathy",
    "achilles_bursitis": "Achilles Tendon Bursitis",
    "hammer_toe": "Hammer Toe Deformity",
    "plantar_fibromatosis": "Plantar Fibromatosis",
    "posterior_tibial_tendinosis": "Tibialis Posterior Tendinosis and Tenosynovitis",
    "metatarsophalangeal_joint_pain": "Metatarsophalangeal Joint Pain",
    "forefoot_pain_metatarsalgia": "Pain in the Ball of the Foot (Metatarsalgia)",
    "tarsal_tunnel_syndrome": "Tarsal Tunnel Syndrome",
    "sesamoiditis": "Sesamoiditis",
    "severs_disease": "Sever Disease (Calcaneal Apophysitis)",
    "inferior_calcaneal_bursitis": "Inferior Calcaneal Bursitis",
    "freiberg_disease": "Freiberg Disease",
    "plantar_nerve_compression": "Medial and Lateral Plantar Nerve Entrapment",
}

QUERY_EN = {
    "q24": "Heel pain in the morning",
    "q25": "My big toe deviates inward and there is a painful bump at its base.",
    "q26": "My 12-year-old son has heel pain after sports.",
    "q27": "How to make homemade bread?",
    "q28": "I have pain behind the heel that gets worse when running, and the area is thickened.",
    "q29": "I have a burning pain in the ball of my foot when walking.",
    "q30": "How do you treat an ingrown toenail?",
}

def run():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    kb_total = 0
    kb_hits = 0

    for q in questions:
        if MODE == "multi":
            results = search_multi(q["question"])
        elif MODE == "multi_en":
            results = search_multi(QUERY_EN.get(q["id"], q["question"]))
        elif MODE == "enriched":
            results = search_enriched(QUERY_EN.get(q["id"], q["question"]))
        else:
            results = search(QUERY_EN.get(q["id"], q["question"]))
        titles = [r["title"] for r in results]
        best = round(results[0]["distance"], 2)

        if q["expected_behavior"] == "kb":
            expected = {ID_TO_TITLE[i] for i in q["expected_ids"]}
            hit = any(t in expected for t in titles)
            kb_total += 1
            kb_hits += hit
            status = "HIT " if hit else "MISS"
        else:
            status = q["category"]

        print(f"{q['id']} {status} d1={best} {titles}")

    print(f"\nhit@3: {kb_hits}/{kb_total}")


if __name__ == "__main__":
    run()