# Hand labels for faithfulness (v6 and v7 answers)

Each sentence of an agent answer is compared with the cited knowledge-base documents.

- **OK**: the document says it clearly.
- **PARTIAL**: the document says something close, but the answer adds a detail.
- **NO**: absent from the documents, or contradicted by them.

These labels are the reference used to check the automatic judge.

## q06 (Achilles Tendinopathy + Achilles Tendon Bursitis)

| # | Sentence | Label | Why |
| --- | --- | --- | --- |
| 1 | Stiffness, pain when starting to run and a thickened feel are common in tendinopathy or bursitis | PARTIAL | "Pain that increases when exercise begins" is in the document. "Stiffness" and "thickened" are not; only "swelling" (bursitis) comes close. |
| 2 | Both involve the tendon and come from repetitive strain from running | NO | Bursitis is inflammation of a bursa, not the tendon, and comes from shoe pressure, not running. "Degenerated" is not in the documents. |
| 3 | Rest and reduce the load on the tendon | OK | "Avoiding running and cycling while pain persists" |
| 4 | Ice after activity | PARTIAL | "Ice" is in the document, "after activity" is not. |
| 5 | Strengthening, especially eccentric heel-drop exercises | PARTIAL | "Eccentric exercise" is in the document, "heel-drop" is an extra detail, and the document presents it to prevent a new injury. |
| 6 | Shoes with a flexible sole or a heel lift | OK | Word for word in the Achilles tendinopathy document. |
| 7 | These measures relieve pain and promote healing | PARTIAL | "Relieve pain" is in the document, "promote healing" is not. |

## q10 (Tibialis Posterior Tendinosis and Tenosynovitis)

| # | Sentence | Label | Why |
| --- | --- | --- | --- |
| 1 | Flattening arch, inner ankle pain and an outward-tilting heel are linked to the tibialis posterior tendon, which supports the arch | PARTIAL | The agent only saw the indexed fields: "gradual" arch loss comes from the complications field, and hindfoot valgus is listed as a cause, not as a heel tilting outward. |
| 2 | When the tendon is weakened or inflamed, the arch can collapse, the ankle may tilt outward and pain appears behind the medial malleolus and along the inner foot | PARTIAL | Arch collapse and pain behind the malleolus are in the document. Hindfoot valgus is listed as a cause, not a consequence: the answer reverses cause and effect. |
| 3 | Orthotics supporting the arch | OK | "Orthotics to support the arch" |
| 4 | Stretching and strengthening exercises | NO | No exercise appears in the treatment of this document. |
| 5 | Modify activity to avoid high-impact movements | NO | The document only says activity triggers the pain; it does not recommend changing it. |
| 6 | In advanced cases, immobilization or surgery | OK | "Immobilization depending on severity", "Surgery for rupture or advanced disease" |

## q32 (Tibialis Posterior Tendinosis and Tenosynovitis), v7 answer

| # | Sentence | Label | Why |
| --- | --- | --- | --- |
| 1 | The symptoms are typical of tibialis posterior tendinosis and tenosynovitis | PARTIAL | "Inward rolling of the foot" is not a symptom in the document (pronation is listed as a cause), and "typical of" is stronger than "most common causes of pain behind the medial malleolus". |
| 2 | The condition involves inflammation of the tendon and its synovial sheath, causing swelling, difficulty walking and rising on the toes | NO | The document says tendinosis is degenerative and only tenosynovitis is inflammation of the sheath: the mechanism is wrong. Also "severely damaged" instead of "fully torn". |
| 3 | Orthotic support, immobilization, anti-inflammatory measures and, in refractory cases, surgery | PARTIAL | The four treatments are in the document, but surgery is for "rupture or advanced disease", not "refractory cases". |

## q34 (Achilles Tendon Bursitis), v7 answer

| # | Sentence | Label | Why |
| --- | --- | --- | --- |
| 1 | Most consistent with posterior Achilles tendon bursitis, irritated by pressure from a high-heeled shoe | OK | Posterior bursa and pressure from heels are in the document ("most consistent with" is diagnostic wording). |
| 2 | The swelling is tender, warm, may appear reddish, especially where the shoe rubs | PARTIAL | Swelling, warmth, tenderness and an erythematous nodule are in the document. "Especially where the shoe rubs" is not. |
| 3 | Caused by pressure from a rigid heel counter or shoes narrowing toward the back of the heel | OK | Taken almost word for word from the causes. |
| 4 | Lower heel or more cushioned heel counter, heel pad or cushion, avoid pumps for a while | PARTIAL | "Low heels, well-fitted" and "relief of pressure" are in the document. "More cushioned", "heel pad or cushion" and "for a while" are added (grey zone: strictly a NO under rule 11). |
| 5 | Anti-inflammatory approach or a local glucocorticoid injection | NO | The document says the injection is possible "for anterior bursitis"; the answer just concluded posterior bursitis and drops the restriction. |

## Summary

21 sentences: 6 OK, 10 PARTIAL, 5 NO. The answers of q06 and q10 come from the v6 run, those of q32 and q34 from the v7 run. All four answers were scored PASS by `score_eval.py`: citing the right source does not guarantee a faithful answer.