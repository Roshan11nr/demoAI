
import os
from dotenv import load_dotenv

import streamlit as st
from ssa import db
from ssa.graph import run_decomposition

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI Goal Mentor — Iteration 1", page_icon="🎯", layout="wide")
st.title("🎯 Empathy‑Driven Chat Companion — Iteration 1")

db.init_db()

# --- Sidebar: Create goal (US-1) ---
st.sidebar.header("Create SMART Goal (US‑1)")
with st.sidebar.form("goal_form", clear_on_submit=True):
    g_title = st.text_input("Goal title*", placeholder="Reduce stress with daily habits")
    g_why = st.text_area("Why it matters", placeholder="Improve well-being and focus")
    g_deadline = st.date_input("Deadline (optional)")
    g_metric = st.text_input("Success metric (optional)", placeholder="At least 5 daily check-ins/week")
    submitted = st.form_submit_button("Save Goal ✅")
    if submitted:
        if not g_title.strip():
            st.sidebar.error("Please enter a goal title.")
        else:
            gid = db.save_goal(g_title.strip(), g_why.strip() or None, str(g_deadline) or None, g_metric.strip() or None)
            st.sidebar.success(f"Saved goal #{gid}")

st.sidebar.divider()
st.sidebar.subheader("Recent Goals")
for row in db.list_goals():
    st.sidebar.write(f"#{row[0]} — **{row[1]}** · due: {row[2]} · {row[3]}")

# --- Main: Tabs ---
tab1, tab2, tab3 = st.tabs(["Decompose (US‑2)", "Plan (US‑3)", "Tasks (US‑4)"])

with tab1:
    st.subheader("Automatic Goal Decomposition (US‑2)")
    selected_goal_id = st.number_input("Goal ID to decompose", min_value=1, step=1, format="%d")
    if st.button("Decompose with LangGraph"):
        if not API_KEY:
            st.error("Missing OPENAI_API_KEY in .env")
        else:
            goal_row = db.get_goal(int(selected_goal_id))
            if not goal_row:
                st.error("Goal not found.")
            else:
                goal_text = goal_row[1]
                subtasks = run_decomposition(API_KEY, goal_text)
                if subtasks:
                    db.add_tasks(int(selected_goal_id), subtasks)
                    st.success(f"Added {len(subtasks)} subtasks for goal #{selected_goal_id}")
                else:
                    st.warning("No subtasks returned; try again.")

with tab2:
    st.subheader("Editable Task Plan (US‑3)")
    goal_id = st.number_input("Goal ID", min_value=1, step=1, format="%d", key="plan_gid")
    tasks = db.list_tasks(int(goal_id)) if goal_id else []
    if not tasks:
        st.info("No tasks yet for this goal.")
    else:
        edited = []
        to_delete = []
        for tid, title, order_idx, status in tasks:
            c1, c2, c3, c4 = st.columns([5,2,2,1])
            with c1:
                new_title = st.text_input(f"Task #{tid}", value=title, key=f"title_{tid}")
            with c2:
                new_order = st.number_input("Order", value=int(order_idx), step=1, key=f"order_{tid}")
            with c3:
                st.write(f"Status: `{status}`")
            with c4:
                if st.checkbox("Delete", key=f"del_{tid}"):
                    to_delete.append(tid)
            edited.append((tid, new_title, int(new_order)))

        cta1, cta2 = st.columns(2)
        if cta1.button("💾 Save Changes"):
            db.update_tasks(edited)
            st.success("Task edits saved.")
        if cta2.button("🗑️ Delete Selected"):
            db.delete_tasks(to_delete)
            st.success(f"Deleted {len(to_delete)} task(s).")

with tab3:
    st.subheader("Task Completion Tracking (US‑4)")
    goal_id2 = st.number_input("Goal ID", min_value=1, step=1, format="%d", key="tasks_gid")
    tasks2 = db.list_tasks(int(goal_id2)) if goal_id2 else []
    if not tasks2:
        st.info("No tasks yet for this goal.")
    else:
        for tid, title, order_idx, status in tasks2:
            done = st.checkbox(f"#{order_idx:02d} {title}", value=(status == "done"), key=f"done_{tid}")
            new_status = "done" if done else "pending"
            if new_status != status:
                db.set_task_status(tid, new_status)
        ratio = db.completion_ratio(int(goal_id2))
        st.progress(ratio, text=f"{round(ratio*100)}% complete")

st.caption("Iteration 1 implements Stories 1–4. Extend in Iteration 2 with mood check‑ins, empathy responses, charts, etc.")

