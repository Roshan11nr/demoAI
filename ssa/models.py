

from pydantic import BaseModel, Field
from typing import List, Optional

class Goal(BaseModel):
    id: int | None = None
    title: str
    why: str | None = None
    deadline: str | None = None  # ISO date
    metric: str | None = None
    status: str = "active"

class Task(BaseModel):
    id: int | None = None
    goal_id: int
    title: str
    order_index: int = 0
    status: str = "pending"  # pending|done
