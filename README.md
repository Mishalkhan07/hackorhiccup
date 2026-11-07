# HackOrHiccup - "Hacked or just broken?" phone triage expert system

Rule-based expert system (forward chaining + point scoring) with a Streamlit UI.
78 rules / 146 conditions across 6 groups: Battery, Data, Apps, Accounts, SIM, Privacy.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py
    python tests/test_cases.py     # run test cases

## Files
- rules.py   - knowledge base (symptoms, verdicts, 78 rules as data)
- engine.py  - forward-chaining inference engine + scoring + rule validation
- report.py  - downloadable report
- app.py     - Streamlit UI
- tests/     - scenario tests

## Deploy (live link)
1. Push this folder to a public GitHub repo.
2. share.streamlit.io -> New app -> pick repo, branch, main file `app.py` -> Deploy.
3. Open the generated URL on mobile data to confirm it works over the internet.
