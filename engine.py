"""
engine.py - Forward-chaining inference engine with point-based scoring.

Pipeline:  symptoms -> working memory -> fire rules until no new fact appears
           -> add up points per verdict -> pick verdict + confidence.
"""
from dataclasses import dataclass, field
from typing import Optional

from rules import RULES, VERDICTS, ATTACK_VERDICTS, SYMPTOMS, CONTEXT_FACTS

ATTACK_THRESHOLD = 25      # minimum points before an attack is declared
SECONDARY_THRESHOLD = 20   # runner-up shown as "also check" above this
AGE_FACTS = {"Under 1 year": "new_device", "1-2 years": "mid_device", "3+ years": "old_device"}
PLATFORM_FACTS = {"Android": "android", "iPhone": "iphone"}


def validate_rules():
    """Sanity-check the knowledge base (called at import time)."""
    derived = {r["derive"] for r in RULES if r["derive"]}
    user_facts = set(SYMPTOMS) | CONTEXT_FACTS
    known = user_facts | derived
    seen = set()
    for r in RULES:
        if r["id"] in seen:
            raise ValueError(f"duplicate rule id {r['id']}")
        seen.add(r["id"])
        for c in r["if"]:
            name = c[1:] if c.startswith("!") else c
            if name not in known:
                raise ValueError(f"{r['id']}: unknown fact '{name}'")
            if c.startswith("!") and name not in user_facts:
                raise ValueError(f"{r['id']}: negation only allowed on user-reported facts")
        if r["verdict"]:
            if r["verdict"] not in VERDICTS or r["points"] <= 0:
                raise ValueError(f"{r['id']}: bad verdict/points")
        elif not r["derive"]:
            raise ValueError(f"{r['id']}: rule does nothing")


validate_rules()


@dataclass
class Result:
    verdict: str
    scores: dict
    confidence: int
    strength: str
    fired: list = field(default_factory=list)      # rules in firing order, each with "round"
    derived: list = field(default_factory=list)    # intermediate facts inferred
    also_check: Optional[str] = None
    facts: set = field(default_factory=set)


def build_facts(symptoms, age="1-2 years", platform="Android"):
    facts = {s for s in symptoms if s in SYMPTOMS}
    facts.add(AGE_FACTS.get(age, "mid_device"))
    facts.add(PLATFORM_FACTS.get(platform, "android"))
    return facts


def _satisfied(rule, memory):
    for c in rule["if"]:
        if c.startswith("!"):
            if c[1:] in memory:
                return False
        elif c not in memory:
            return False
    return True


def forward_chain(facts):
    """Fire rules repeatedly until a full pass derives no new fact."""
    memory, fired, fired_ids, derived = set(facts), [], set(), []
    round_no, changed = 0, True
    while changed:
        changed = False
        round_no += 1
        for r in RULES:
            if r["id"] in fired_ids or not _satisfied(r, memory):
                continue
            fired_ids.add(r["id"])
            fired.append({**r, "round": round_no})
            if r["derive"] and r["derive"] not in memory:
                memory.add(r["derive"])
                derived.append(r["derive"])
                changed = True
    return memory, fired, derived


def diagnose(symptoms, age="1-2 years", platform="Android"):
    facts = build_facts(symptoms, age, platform)
    memory, fired, derived = forward_chain(facts)

    scores = {v: 0 for v in ATTACK_VERDICTS + ["NORMAL_FAULT"]}
    for r in fired:
        if r["verdict"]:
            scores[r["verdict"]] += r["points"]
    total = sum(scores.values())

    top_attack = max(ATTACK_VERDICTS, key=lambda v: scores[v])
    attack_pts, normal_pts = scores[top_attack], scores["NORMAL_FAULT"]

    if attack_pts >= ATTACK_THRESHOLD and attack_pts >= normal_pts:
        verdict, top = top_attack, attack_pts
    elif normal_pts > 0 and normal_pts >= attack_pts:
        verdict, top = "NORMAL_FAULT", normal_pts
    else:
        verdict, top = "INCONCLUSIVE", 0

    confidence = round(100 * top / total) if total and top else 0
    strength = "Strong" if top >= 70 else "Moderate" if top >= 40 else "Weak"

    also = None
    others = sorted(((scores[v], v) for v in scores if v != verdict), reverse=True)
    if verdict != "INCONCLUSIVE" and others and others[0][0] >= SECONDARY_THRESHOLD:
        also = others[0][1]

    return Result(verdict, scores, confidence, strength, fired, derived, also, memory)
