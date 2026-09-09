"""PromptSpec A/B templates with {input} placeholders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptSpec:
    """A named system/user template pair.

    Templates use Python ``str.format`` placeholders. Built-in demos only
    require ``{input}``; extra keys raise ``KeyError`` at render time.
    """

    name: str
    system: str
    user: str = "{input}"

    def render(self, **kwargs: str) -> tuple[str, str]:
        """Return (system, user) with placeholders filled."""
        try:
            system = self.system.format(**kwargs)
            user = self.user.format(**kwargs)
        except KeyError as exc:
            raise KeyError(
                f"prompt {self.name!r} missing placeholder {exc.args[0]!r}"
            ) from exc
        return system, user


# Vague A: soft instructions, invites waffle.
PROMPT_A = PromptSpec(
    name="A_vague",
    system=(
        "You help a small shop. Classify this customer message somehow. "
        "Be helpful and say a few words."
    ),
)

# Clear B: exact labels, one-token reply — specificity wins.
PROMPT_B = PromptSpec(
    name="B_specific",
    system=(
        "You are an intent classifier for a small shop help desk. "
        "Reply with EXACTLY one label and nothing else. "
        "Allowed labels: return, hours, escalate, other."
    ),
)


def default_prompts() -> tuple[PromptSpec, PromptSpec]:
    return PROMPT_A, PROMPT_B
