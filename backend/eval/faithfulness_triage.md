# Triage of the judge's NO sentences (v6 and v7)

The automatic judge labels a sentence NO when the cited fiches do not support it. Reading these sentences by hand (by a podiatrist) shows that many NO are not unfaithful claims. Each NO was classified as:

- **INVENTION**: a treatment, advice or medical fact that is not in the fiches.
- **ERROR**: contradicts the fiches or is clinically inaccurate.
- **FALSE ALARM**: advice to consult a professional, disclaimer, meta sentence, or the answer listing candidate conditions.
- **WORDING**: diagnostic phrasing, not a faithfulness problem (tracked separately by `diagnosis_phrases.py`).

## v6 (9 NO sentences, 23 answers)

| Question | Sentence (shortened) | Class |
| --- | --- | --- |
| q01 | This is an educational overview; it is not a diagnosis. | FALSE ALARM |
| q04 | A podiatrist can examine him to confirm the diagnosis | FALSE ALARM |
| q06 | Both conditions involve the tendon... can become inflamed | ERROR (bursitis involves the bursa, not the tendon) |
| q06 | Please consult a podiatrist... | FALSE ALARM |
| q10 | Stretching and strengthening exercises | INVENTION |
| q10 | Activity modification to avoid high-impact movements | INVENTION |
| q22 | The appropriate dose depends on weight, kidney function... | INVENTION (harmless, from model memory) |
| q28 | Einen Podologen oder Orthopäden aufzusuchen | FALSE ALARM |
| q36 | It is important to see a healthcare professional | FALSE ALARM |

Real NO: 4 sentences in 3 answers out of 23 (13%).

## v7 (10 NO sentences, 23 answers, rule 11 active)

| Question | Sentence (shortened) | Class |
| --- | --- | --- |
| q03 | It often causes the toe to rub... leading to a corn | minor deviation (repeats the patient's description), not counted |
| q03 | A podiatrist can trim or remove it; self-removal is not recommended | INVENTION (clinically sound) |
| q05 | ...custom orthotics or targeted exercises | INVENTION (targeted exercises) |
| q06 | It sounds like you may have an issue with... | WORDING |
| q11 | Two common foot-related causes are: | INVENTION (second cause comes from model memory; wrong sources) |
| q14 | I do not have additional specific information... | FALSE ALARM |
| q24 | Consulter un professionnel de santé spécialisé en podologie | FALSE ALARM |
| q25 | Le gros orteil... dévie vers l'intérieur... typiquement un bunion | ERROR, to be confirmed clinically (direction of the deviation repeated from the patient) |
| q31 | ...rule out other conditions such as a stress fracture or nerve irritation | INVENTION (differential diagnoses from model memory) |
| q33 | It could be sesamoiditis or metatarsophalangeal joint pain. | FALSE ALARM |

Real NO: 5 sentences in 5 answers out of 23 (22%).

## Reading

- The raw judge counts (9 NO in 7 answers for v6, 10 NO in 9 answers for v7) overstate the problem: 5 of 9 and 4 of 10 NO are false alarms.
- After triage, the rate of answers with a real NO goes from 13% (v6) to 22% (v7). With 23 answers and a judge that changes about 2 sentences out of 7 between two runs, this difference is within the noise: rule 11 is neither shown to help nor to hurt on this measure.
- What rule 11 did change: the exercises and activity advice invented in q10 disappeared. New leaks appeared elsewhere (q03, q05), and differential diagnoses from memory (q31) are outside the rule.