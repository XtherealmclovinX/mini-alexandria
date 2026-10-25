# core/worker.py — question in, draft out.
# The chosen agent answers, the draft is saved to data/inbox/,
# and each line of what happened is printed so the learner can follow.

import os
import time

from . import llm, memory, router, runs

BASE = os.path.dirname(os.path.dirname(__file__))
INBOX = os.path.join(BASE, "data", "inbox")


def run_task(llm_client, task, config, do_review=False, source="cli"):
    """The full pipeline for one task: route -> draft -> (review -> revise).

    Returns the final text of the answer.
    """
    started = time.time()
    stamp = time.strftime("%Y-%m-%d_%H%M%S")
    recent = memory.recall(config["memory_chars_per_task"])

    role = router.route(llm_client, task, config["roster"])
    print("[route] task assigned to: " + role)
    print("[working] " + task)

    memory_context = ""
    if recent:
        memory_context = (
            "\n\n--- Recent memory (what already happened this week) ---\n"
            + recent + "\n--- end of recent memory ---"
        )

    system = router.build_system(role)
    user = task + memory_context
    answer = llm_client.chat(
        system=system,
        user=user,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        timeout=config["timeout_seconds"],
    )

    if do_review:
        print("[review] asking the VP of Review to check this draft")
        from . import review as review_mod
        critique = review_mod.critique(llm_client, task, answer, config)
        if critique.issues:
            print("[review] issues found: " + ", ".join(critique.issues))
            answer = review_mod.revise(llm_client, task, answer, critique.text, config)
        else:
            print("[review] no issues flagged")

    if not os.path.isdir(INBOX):
        os.makedirs(INBOX)
    path = os.path.join(INBOX, stamp + "-" + role + ".md")
    with open(path, "w") as handle:
        handle.write(time.strftime("%Y-%m-%d %H:%M:%S\n") + "task: " + task + "\n---\n" + answer + "\n")
    print("[saved] " + path)

    memory.remember(role, task, answer[:400])
    runs.record(source, role, time.time() - started, do_review)
    return answer