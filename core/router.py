# core/router.py — the Chief of Staff decides WHO handles a task.
# One small question to the model: "which agent should take this?"

import os

from . import llm

AGENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents")


def read_agent(name):
    path = os.path.join(AGENTS_DIR, name + ".md")
    with open(path, "r") as handle:
        return handle.read()


def route(llm_client, task, roster):
    """Return the name of the agent that should handle `task`.

    roster lists the four specialists; 'chief' is the fallback when the
    model answers anything unexpected (small models misroute sometimes —
    this keeps the team usable anyway).
    """
    options = "\n".join("- " + name for name in roster)
    system = read_agent("chief")
    user = (
        "Available agents:\n" + options +
        "\n\nPick exactly one agent name from the list above to handle "
        "the task below. Reply with ONLY the name, nothing else.\n\n"
        "Task: " + task
    )
    answer = llm_client.chat(
        system=system,
        user=user,
        max_tokens=12,
        temperature=0.1,
        timeout=120,
    )
    answer = answer.strip().lower().split()[0].strip("-*# ") if answer else ""
    if answer in roster:
        return answer
    return "chief"


def build_system(role):
    """Agent system prompt = shared foundation + that agent's mission."""
    return read_agent("global") + "\n\n---\n\n" + read_agent(role)