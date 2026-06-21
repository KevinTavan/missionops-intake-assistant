import os
from typing import Optional


SYSTEM_PROMPT = """You are a careful intake support assistant for a mission-driven organization.

You organize messy intake notes into a structured, reviewable staff brief. You do not make final decisions. You do not provide legal, medical, housing, or benefits determinations. You mark missing information as missing instead of guessing.

Return markdown with these sections:
1. Summary
2. Need Categories
3. Urgency
4. Evidence From Source Note
5. Missing Information to Confirm
6. Suggested Next Steps
7. Human Review Checklist
"""


def claude_available() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def analyze_with_claude(note: str, model: Optional[str] = None) -> str:
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise ImportError("The anthropic package is not installed. Run pip install -r requirements.txt.") from exc

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    selected_model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    message = client.messages.create(
        model=selected_model,
        max_tokens=1200,
        temperature=0.2,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Source intake note:\n\n{note}\n\nCreate the structured brief."
            }
        ],
    )

    return "\n".join(block.text for block in message.content if hasattr(block, "text"))
