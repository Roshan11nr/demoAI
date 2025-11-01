
from typing import List
from openai import OpenAI
from langgraph.graph import StateGraph, START, END

# A minimal state dict for langgraph
class DecomposeState(dict):
    goal: str
    subtasks: List[str]

def _call_openai_for_subtasks(api_key: str, goal: str) -> List[str]:
    client = OpenAI(api_key=api_key)
    prompt = (
        "Break the user's single goal into 5-10 tiny, safe, daily subtasks. "
        "Return them as a JSON list of short imperative strings only."
        f"\nGoal: {goal}"
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    # Expected shape: {"items": ["subtask1", ...]}
    try:
        import json
        data = json.loads(resp.choices[0].message.content or "{}")
        items = data.get("items") or data.get("subtasks") or []
        # Fallback: if model returned a bare array string
        if isinstance(items, list):
            return [str(x) for x in items][:10]
        elif isinstance(data, list):
            return [str(x) for x in data][:10]
    except Exception:
        pass
    # Very defensive fallback
    return [f"Define scope for: {goal}", "List 5 actions", "Do the smallest action"]

def build_graph(api_key: str):
    def decompose(state: DecomposeState):
        goal = state.get("goal", "")
        subtasks = _call_openai_for_subtasks(api_key, goal)
        state["subtasks"] = subtasks
        return state

    g = StateGraph(DecomposeState)
    g.add_node("decompose", decompose)
    g.add_edge(START, "decompose")
    g.add_edge("decompose", END)
    return g.compile()

def run_decomposition(api_key: str, goal_text: str) -> list[str]:
    graph = build_graph(api_key)
    out = graph.invoke({"goal": goal_text})
    return out.get("subtasks", []) or []
