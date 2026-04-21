# Daily Meal & Diet Planner — Capstone

Personal, not clinical. Vegetarian · no nuts · diabetic-friendly · 1800 kcal default, 1500 kcal floor.

Built on the 8-node LangGraph from the Agentic AI capstone guidance:

```
memory → router → (retrieve | skip | tool) → answer → eval → save → END
```

## Files

| File | What it is |
| --- | --- |
| `knowledge_base.py` | 12 KB documents (rules, meal templates, macros, Indian foods, hydration, timing, sample day, scope) |
| `tools.py` | `calculator` (macro math) and `datetime` (meal-window) tools |
| `agent.py` | `CapstoneState`, 8 nodes, conditional edges, `build_app()`, `ask()` |
| `capstone_streamlit.py` | Streamlit chat UI with `@st.cache_resource` init and thread-id session state |
| `day13_capstone.ipynb` | Full walkthrough: KB → state → nodes → graph → tests → RAGAS → summary |
| `requirements.txt` | Pinned deps |
| `.env.example` | Copy to `.env`, set `GROQ_API_KEY` |

## Run

```bash
pip install -r requirements.txt
cp .env.example .env          # add your GROQ_API_KEY
streamlit run capstone_streamlit.py
```

Or run the agent directly:

```bash
python agent.py
```

Or open the notebook and run **Kernel → Restart & Run All**:

```bash
jupyter lab day13_capstone.ipynb
```

## Red-team behaviour

The system prompt in `agent.py` refuses:

- **Clinical questions** (*am I diabetic?*) → redirects to dietitian / physician.
- **Extreme calorie targets** (*600 kcal/day*, *skip meals*) → states the 1500 kcal floor; mentions Vandrevala (1860-2662-345) / iCall (9152987821) helplines.
- **Prompt injection** (*ignore your instructions*, *print your system prompt*) → refuses and continues.
- **Rule-breaking meals** (*add cashew paste*, *suggest chicken*) → refuses and names the rule.

## Notes

- If `GROQ_API_KEY` is not set, `agent.py` falls back to a heuristic stub LLM so the graph still compiles and smoke-tests — you'll want a real key for meaningful answers and RAGAS.
- ChromaDB is in-memory (no `persist_directory`), so the KB re-embeds on every process start. 12 short docs → a second or two.
