# core/review.py — the VP of Review pass.
# Review is a separate QUESTION to the same model, wearing the review
# agent's mission. It returns critique.issues (a list) and critique.text
# (the full notes). If anything is flagged, the worker does ONE revise pass.

from . import router

CHECKS = (
    "fabrication (claims, numbers or studies that may be invented),",
    "missing safety/legal disclaimer where it matters,",
    "vagueness (no concrete next step),",
    "answering a different question than asked."
)


class Critique:
    def __init__(self, issues, text):
        self.issues = issues
        self.text = text


def critique(llm_client, task, draft, config):
    system = router.build_system("review")
    user = (
        "Original task: " + task + "\n\nDraft to review:\n" + draft +
        "\n\nCheck the draft for: " + " ".join(CHECKS) +
        "\nReply on the FIRST line with either: ISSUES NONE  (or)  ISSUES: one, two, three"
    )
    raw = llm_client.chat(
        system=system,
        user=user,
        max_tokens=config["max_tokens"],
        temperature=0.2,
        timeout=config["timeout_seconds"],
    )
    first = raw.splitlines()[0].upper() if raw else ""
    if "NONE" in first:
        return Critique([], raw)
    return Critique(["flagged"], raw)


def revise(llm_client, task, draft, critique_text, config):
    system = router.build_system("review")
    user = (
        "Task: " + task + "\n\nYour draft:\n" + draft +
        "\n\nReview notes:\n" + critique_text +
        "\n\nRewrite the draft with every valid note in the review applied. "
        "Reply with ONLY the improved draft."
    )
    return llm_client.chat(
        system=system,
        user=user,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        timeout=config["timeout_seconds"],
    )