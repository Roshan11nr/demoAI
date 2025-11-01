
import sqlite3
from contextlib import contextmanager
from typing import Iterable, List, Tuple, Optional, Dict, Any

DB_PATH = "mentor.db"

@contextmanager
def connect(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with connect() as conn:
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                title TEXT,
                why TEXT,
                deadline TEXT,
                metric TEXT,
                status TEXT DEFAULT 'active'
            );'''
        )
        c.execute(
            '''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER,
                title TEXT,
                order_index INTEGER,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY(goal_id) REFERENCES goals(id)
            );'''
        )

def save_goal(title: str, why: str | None, deadline: str | None, metric: str | None) -> int:
    from datetime import datetime
    with connect() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO goals (created_at, title, why, deadline, metric) VALUES (?,?,?,?,?)",
            (datetime.utcnow().isoformat(), title, why, deadline, metric),
        )
        return c.lastrowid

def list_goals(limit: int = 20) -> list[tuple]:
    with connect() as conn:
        return conn.execute(
            "SELECT id, title, deadline, status FROM goals ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

def get_goal(goal_id: int) -> tuple | None:
    with connect() as conn:
        return conn.execute(
            "SELECT id, title, why, deadline, metric, status FROM goals WHERE id=?",
            (goal_id,),
        ).fetchone()

def add_tasks(goal_id: int, titles: list[str]):
    with connect() as conn:
        c = conn.cursor()
        for idx, t in enumerate(titles):
            c.execute(
                "INSERT INTO tasks (goal_id, title, order_index) VALUES (?,?,?)",
                (goal_id, t.strip(), idx),
            )

def list_tasks(goal_id: int) -> list[tuple]:
    with connect() as conn:
        return conn.execute(
            "SELECT id, title, order_index, status FROM tasks WHERE goal_id=? ORDER BY order_index ASC",
            (goal_id,),
        ).fetchall()

def update_tasks(edits: list[tuple[int, str, int]]):
    # edits: list of (task_id, new_title, new_order_index)
    with connect() as conn:
        for tid, title, order_idx in edits:
            conn.execute(
                "UPDATE tasks SET title=?, order_index=? WHERE id=?",
                (title, order_idx, tid),
            )

def delete_tasks(task_ids: list[int]):
    if not task_ids:
        return
    with connect() as conn:
        q = "DELETE FROM tasks WHERE id IN (%s)" % ",".join("?" * len(task_ids))
        conn.execute(q, task_ids)

def set_task_status(task_id: int, status: str):
    with connect() as conn:
        conn.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))

def completion_ratio(goal_id: int) -> float:
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM tasks WHERE goal_id=?", (goal_id,)).fetchone()[0]
        if total == 0:
            return 0.0
        done = conn.execute("SELECT COUNT(*) FROM tasks WHERE goal_id=? AND status='done'", (goal_id,)).fetchone()[0]
        return done / total
