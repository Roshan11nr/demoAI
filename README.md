


# Empathy‑Driven Chat Companion (AI Goal Mentor) — Iteration 1

This repository implements **User Stories 1–4** for your *Empathy‑Driven Chat Companion (AI Goal Mentor for Emotional Well‑Being)*.
It includes a minimal **Streamlit** UI, a **LangGraph**-based goal decomposition step, and a local **SQLite** data layer.

## What’s included (Iteration 1 scope)

- ✅ **User Story 1 – Goal Input and Storage**: save SMART goal fields to SQLite.
- ✅ **User Story 2 – Automatic Goal Decomposition**: one-click decomposition via a tiny LangGraph graph that yields 5–10 subtasks and saves them.
- ✅ **User Story 3 – Editable Task Plan**: inline edit task names and order; delete tasks; changes persist.
- ✅ **User Story 4 – Task Completion Tracking**: per-task checkbox + progress bar; state persists.

> Outside Iteration 1: mood check‑ins, empathy library, charts, etc., can be added next iteration.

## Quickstart

1) **Install** (Python 3.10+ recommended):
```bash
pip install -r requirements.txt
```

2) Create **.env** from the template and add your key:
```bash
cp .env.example .env
# then edit .env to put your OPENAI_API_KEY
```

3) **Run** the app:
```bash
streamlit run app.py
```

## Repository layout

```
ai-goal-mentor-iteration1/
├─ app.py                # Streamlit UI wiring Stories 1–4
├─ ssa/
│  ├─ __init__.py
│  ├─ db.py              # SQLite schema + helpers
│  ├─ graph.py           # LangGraph: decompose goal into subtasks
│  └─ models.py          # Pydantic data models
├─ tests/
│  └─ test_smoke.py      # Smoke tests for DB + decomposition shape
├─ requirements.txt
├─ .env.example
├─ .gitignore
└─ README.md
```

## Mapping to User Stories (Iteration 1)

- **US‑1 Goal Input & Storage**: `app.py` sidebar form → `ssa/db.py@save_goal()`; visible in “Goals” table.
- **US‑2 Automatic Goal Decomposition**: “Decompose with LangGraph” button → `ssa/graph.py@run_decomposition()` persists subtasks to `tasks` table.
- **US‑3 Editable Task Plan**: “Plan” tab enables inline edits, reordering (order index), and delete – persisted via `update_tasks()`.
- **US‑4 Task Completion Tracking**: checkboxes in “Tasks” tab; progress bar reflects `% complete` for current goal.

## Notes

- Uses **LangGraph** as requested to orchestrate the decomposition node (even though it’s a single‑node graph in Iteration 1).
- Stores data in `mentor.db` in the repo folder by default; safe to delete between runs.
- You can expand the graph with additional nodes in Iteration 2 (e.g., “repair plan”, “ask for constraints”, etc.).

## License

MIT
