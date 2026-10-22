# core/llm.py — the ONLY place mini-alexandria talks to the model.
# ~30 lines on purpose: read it top to bottom and you understand the layer.
# Uses only the Python standard library (no pip installs needed).

import json
import urllib.request


class LLM:
    def __init__(self, base_url, model):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, system, user, max_tokens, temperature, timeout):
        """One question-answer round trip.

        system  = the agent's mission text (from agents/*.md)
        user    = the question or task
        Returns the model's reply text, or raises on error.
        """
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode()

        request = urllib.request.Request(
            self.base_url + "/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                answer = json.loads(response.read())
        except urllib.error.URLError as error:
            raise RuntimeError(
                "Could not reach the model server at " + self.base_url +
                " — did you run: sh start.sh ? (" + str(error) + ")"
            ) from error
        return answer["choices"][0]["message"]["content"].strip()