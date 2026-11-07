"""report.py - builds the downloadable plain-text diagnosis report."""
from datetime import datetime

from rules import VERDICTS, SYMPTOM_LABELS


def make_report(result, symptoms, age, platform):
    v = VERDICTS[result.verdict]
    L = ["HACKORHICCUP - PHONE DIAGNOSIS REPORT",
         datetime.now().strftime("Generated: %Y-%m-%d %H:%M"), "=" * 60,
         f"Device: {platform}, age {age}", "", "SYMPTOMS REPORTED"]
    L += [f"  - {SYMPTOM_LABELS[s]}" for s in symptoms] or ["  (none)"]
    L += ["", "VERDICT", f"  {v['title']}  |  Severity: {v['severity']}",
          f"  Confidence: {result.confidence}%  |  Evidence: {result.strength}", f"  {v['summary']}"]
    if result.also_check:
        L.append(f"  Also check: {VERDICTS[result.also_check]['title']}")
    L += ["", "SCORES"]
    L += [f"  {VERDICTS[k]['title']}: {p} pts" for k, p in sorted(result.scores.items(), key=lambda x: -x[1])]
    L += ["", "RULES THAT FIRED"]
    for r in result.fired:
        tail = f"-> {r['verdict']} +{r['points']}" if r["verdict"] else f"-> fact: {r['derive']}"
        L.append(f"  [{r['id']}] (round {r['round']}) {r['why']} {tail}")
    L += ["", "WHAT TO DO"] + [f"  {i}. {s}" for i, s in enumerate(v["steps"], 1)]
    L += ["", "Note: educational expert system. It is not a forensic tool; for serious cases contact",
          "your network, bank and FIA Cybercrime Wing (NR3C)."]
    return "\n".join(L)
