"""app.py - Streamlit UI for HackOrHiccup (run: streamlit run app.py)"""
import pandas as pd
import streamlit as st

from engine import diagnose
from report import make_report
from rules import RULES, SCENARIOS, SYMPTOM_GROUPS, SYMPTOMS, VERDICTS

st.set_page_config(page_title="HackOrHiccup", page_icon="🛡️", layout="wide")

AGES = ["Under 1 year", "1-2 years", "3+ years"]
PLATFORMS = ["Android", "iPhone"]


st.session_state.setdefault("device_age", "1-2 years")
st.session_state.setdefault("platform", "Android")


def load_scenario(name):
    sc = SCENARIOS[name]
    for sid in SYMPTOMS:
        st.session_state[f"sym_{sid}"] = sid in sc["symptoms"]
    st.session_state["device_age"] = sc["age"]
    st.session_state["platform"] = sc["platform"]
    st.session_state.pop("result", None)


def clear_all():
    for sid in SYMPTOMS:
        st.session_state[f"sym_{sid}"] = False
    st.session_state.pop("result", None)


# ------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("🛡️ HackOrHiccup")
    st.caption("Expert system that tells you whether your phone is **hacked** or just **broken**.")
    st.metric("Rules in knowledge base", len(RULES))
    st.metric("Conditions", sum(len(r["if"]) for r in RULES))
    st.divider()
    st.subheader("Try a demo case")
    for name in SCENARIOS:
        st.button(name, on_click=load_scenario, args=(name,), width="stretch")
    st.button("🧹 Clear all", on_click=clear_all, width="stretch")
    st.divider()
    st.caption("Educational tool. Not a replacement for forensic analysis.")

# ------------------------------------------------------------ inputs
st.title("🛡️ HackOrHiccup")
st.write("**Hacked or just broken?** Tick what you notice. The inference engine chains rules together "
         "and scores each possible cause.")

c1, c2 = st.columns(2)
age = c1.selectbox("Phone age", AGES, key="device_age")
platform = c2.radio("Platform", PLATFORMS, horizontal=True, key="platform")

tabs = st.tabs(list(SYMPTOM_GROUPS))
for tab, (group, items) in zip(tabs, SYMPTOM_GROUPS.items()):
    with tab:
        for sid, label in items:
            st.checkbox(label, key=f"sym_{sid}")

if st.button("🔍 Diagnose my phone", type="primary", width="stretch"):
    chosen = [s for s in SYMPTOMS if st.session_state.get(f"sym_{s}")]
    if not chosen:
        st.warning("Tick at least one symptom first.")
        st.session_state.pop("result", None)
    else:
        st.session_state["result"] = diagnose(chosen, age, platform)
        st.session_state["ctx"] = (chosen, age, platform)

# ------------------------------------------------------------ results
res = st.session_state.get("result")
if res:
    chosen, ctx_age, ctx_platform = st.session_state["ctx"]
    v = VERDICTS[res.verdict]
    box = {"Critical": st.error, "High": st.error, "Medium": st.warning,
           "Low": st.success, "Info": st.info}[v["severity"]]
    box(f"### {v['icon']} {v['title']}\n\n{v['summary']}")
    if res.also_check:
        st.warning(f"Also worth checking: **{VERDICTS[res.also_check]['title']}**")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Confidence", f"{res.confidence}%" if res.confidence else "-")
    m2.metric("Evidence strength", res.strength)
    m3.metric("Severity", v["severity"])
    m4.metric("Rules fired", len(res.fired))

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Score breakdown")
        df = pd.DataFrame({"Verdict": [VERDICTS[k]["title"] for k in res.scores],
                           "Points": list(res.scores.values())}).set_index("Verdict")
        st.bar_chart(df)
    with right:
        st.subheader("What to do now")
        for i, step in enumerate(v["steps"], 1):
            st.markdown(f"{i}. {step}")

    with st.expander("🧠 Why this result? (rules that fired)", expanded=True):
        if res.derived:
            st.caption("Facts inferred by chaining: " + ", ".join(f"`{d}`" for d in res.derived))
        rows = [{"Round": r["round"], "Rule": r["id"], "Group": r["group"], "Because": r["why"],
                 "Effect": f"{VERDICTS[r['verdict']]['title']} +{r['points']}" if r["verdict"] else f"infers {r['derive']}"}
                for r in res.fired]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    st.download_button("📄 Download report", make_report(res, chosen, ctx_age, ctx_platform),
                       file_name="hackorhiccup_report.txt", width="stretch")
