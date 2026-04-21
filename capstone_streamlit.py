"""
Streamlit front-end for the Daily Meal & Diet Planner.

Run:  streamlit run capstone_streamlit.py
"""

from __future__ import annotations

import uuid

import streamlit as st

from agent import build_app
from knowledge_base import DOCUMENTS


# ---------------------------------------------------------------------------
# Cached init — expensive resources must live inside @st.cache_resource so
# Streamlit does NOT rebuild them on every rerun.
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading diet planner agent…")
def get_app():
    return build_app()


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Daily Meal & Diet Planner", page_icon="🥗")
st.title("🥗 Daily Meal & Diet Planner")
st.caption(
    "Vegetarian · no nuts · diabetic-friendly · 1800 kcal default. "
    "Personal, not clinical."
)

# ---- Session state --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session-{uuid.uuid4().hex[:8]}"


# ---- Sidebar --------------------------------------------------------------
with st.sidebar:
    st.header("About this agent")
    st.markdown(
        "Helps you stay consistent with a simple diet:\n\n"
        "- Suggests meals within your rules\n"
        "- Does macro / calorie math on foods it knows\n"
        "- Reminds you about timing and hydration\n\n"
        "**Will not** diagnose conditions, prescribe medication, or plan "
        "extreme calorie cuts (hard floor: 1500 kcal/day)."
    )

    st.subheader("Knowledge base topics")
    for d in DOCUMENTS:
        st.markdown(f"- {d['topic']}")

    st.subheader("Session")
    st.code(st.session_state.thread_id, language="text")
    if st.button("New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = f"session-{uuid.uuid4().hex[:8]}"
        st.rerun()

    st.caption(
        "If you ever feel in distress around food or body image, please "
        "reach out: Vandrevala 1860-2662-345 · iCall 9152987821."
    )


# ---- Chat history ---------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        meta = msg.get("meta")
        if meta:
            with st.expander("trace"):
                st.write(meta)


# ---- Input ----------------------------------------------------------------
prompt = st.chat_input("Ask about meals, macros, timing… (e.g. 'veg dinner under 500 kcal')")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    app = get_app()
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            result = app.invoke(
                {"question": prompt, "eval_retries": 0},
                config=config,
            )
        answer = result.get("answer", "(no answer)")
        st.markdown(answer)
        meta = {
            "route": result.get("route"),
            "sources": result.get("sources"),
            "faithfulness": result.get("faithfulness"),
            "tool": result.get("tool_name"),
            "tool_arg": result.get("tool_arg"),
            "tool_result": result.get("tool_result"),
        }
        with st.expander("trace"):
            st.write(meta)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "meta": meta}
    )
