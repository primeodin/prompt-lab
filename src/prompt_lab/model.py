"""MockModel (deterministic) + optional LiveModel (OpenAI-compatible)."""

from __future__ import annotations

import os
import re
from typing import Protocol

import httpx

# Intent keywords the mock looks for in the user message.
_INTENT_RULES: tuple[tuple[str, str], ...] = (
    (r"\b(return|refund|broken|exchange)\b", "return"),
    (r"\b(hours?|open|close[sd]?|saturday|sunday)\b", "hours"),
    (r"\b(human|agent|person|manager|stuck)\b", "escalate"),
)


def _guess_label(user: str) -> str:
    text = user.lower()
    for pattern, label in _INTENT_RULES:
        if re.search(pattern, text):
            return label
    return "other"


class Model(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class MockModel:
    """Deterministic stand-in so README expected stdout stays stable.

    Behavior is keyed off the *system* prompt quality:
    - If the system asks for EXACTLY one allowed label → emit that label.
    - Otherwise → emit a vague, wordy reply that fails exact_match / length_band.
    """

    def complete(self, system: str, user: str) -> str:
        label = _guess_label(user)
        sys_l = system.lower()
        specific = (
            "exactly one label" in sys_l
            and "allowed labels" in sys_l
            and "return" in sys_l
            and "hours" in sys_l
        )
        if specific:
            return label
        # Vague prompt path — helpful waffle that rarely matches exact_match.
        if label == "return":
            return "Sure — happy to help with that return request when you are ready."
        if label == "hours":
            return "I can look into store timing for you; what day were you thinking?"
        if label == "escalate":
            return "Of course, I understand wanting a person. Let me see what I can do."
        return "Thanks for the message! How else can I assist today?"


class LiveModel:
    """Thin OpenAI-compatible chat wrapper. Unused by tests / --mock."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4o-mini",
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (
            base_url
            or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        ).rstrip("/")
        self.model = model
        self.timeout = timeout
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required for --live "
                "(or pass api_key=...). Tests never need this."
            )

    def complete(self, system: str, user: str) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
