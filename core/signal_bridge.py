# core/signal_bridge.py — PHASE 2 STUB.
# Signal does not run on the phone (it needs Java + ~1GB RAM the model needs).
# When mini-alexandria moves to a computer, this module becomes the real
# bridge: signal-cli on non-Docker machines, or the container JSON-RPC
# pattern on a Docker-capable host (see CLAUDE.md in Alexander's workspace).
# The rest of the code never calls this module until Phase 2 — the import
# is deliberately the only reference.


def send(message_text):
    raise NotImplementedError(
        "Signal arrives in Phase 2, once mini-alexandria moves to a computer."
    )