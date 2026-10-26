# Hand labels for faithfulness (v6 answers)

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
| 7 | These measures relieve pain and promote healing | OK | General sentence, consistent with "relieve pain". |

## q10 (Tibialis Posterior Tendinosis and Tenosynovitis)

| # | Sentence | Label | Why |
| --- | --- | --- | --- |
| 1 | Flattening arch, inner ankle pain and an outward-tilting heel are linked to the tibialis posterior tendon, which supports the arch | OK | Overview: the tendon "helps maintain the normal arch" and is the most common cause of pain behind the medial malleolus. Gradual arch loss is in complications; hindfoot valgus is in causes. |
| 2 | When the tendon is weakened or inflamed, the arch can collapse, the ankle may tilt outward and pain appears behind the medial malleolus and along the inner foot | PARTIAL | Arch collapse and pain behind the malleolus are in the document. Hindfoot valgus is listed as a cause, not a consequence: the answer reverses cause and effect. |
| 3 | Orthotics supporting the arch | OK | "Orthotics to support the arch" |
| 4 | Stretching and strengthening exercises | NO | No exercise appears in the treatment of this document. |
| 5 | Modify activity to avoid high-impact movements | NO | The document only says activity triggers the pain; it does not recommend changing it. |
| 6 | In advanced cases, immobilization or surgery | OK | "Immobilization depending on severity", "Surgery for rupture or advanced disease" |

## Summary

13 sentences: 6 OK, 4 PARTIAL, 3 NO. Both answers were scored PASS by `score_eval.py`.