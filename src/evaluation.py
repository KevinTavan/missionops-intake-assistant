import re
from src.triage_engine import detect_needs, detect_urgency


def extract_numbers(text: str):
    return set(re.findall(r"\b\d+(?:[.,]\d+)?\b", text))


def evaluate_output_against_source(source: str, draft: str) -> str:
    source_needs = set(detect_needs(source))
    draft_needs = set(detect_needs(draft))

    urgency, reasons = detect_urgency(source)

    numbers_source = extract_numbers(source)
    numbers_draft = extract_numbers(draft)
    unsupported_numbers = sorted(numbers_draft - numbers_source)

    missed_needs = sorted(source_needs - draft_needs)
    extra_needs = sorted(draft_needs - source_needs)

    risk_notes = []

    if unsupported_numbers:
        risk_notes.append(f"Draft includes numbers not found in source: {', '.join(unsupported_numbers)}")

    if missed_needs:
        risk_notes.append(f"Draft may have missed source need categories: {', '.join(missed_needs)}")

    if extra_needs:
        risk_notes.append(f"Draft may introduce need categories not clearly found in source: {', '.join(extra_needs)}")

    draft_l = draft.lower()

    if "not specified" not in draft_l and "missing" not in draft_l and "confirm" not in draft_l:
        risk_notes.append("Draft may not clearly mark missing information or needed confirmation.")

    if "High" in urgency and not any(term in draft_l for term in ["urgent", "high", "escalat", "prompt review", "soon"]):
        risk_notes.append("Source has urgent risk indicators, but draft may not flag urgency strongly enough.")

    score = max(1, 5 - min(len(risk_notes), 4))

    if not risk_notes:
        risk_notes.append("No major lightweight-evaluation issues detected. Human review still required.")

    source_need_text = ", ".join(sorted(source_needs)) if source_needs else "None detected"
    draft_need_text = ", ".join(sorted(draft_needs)) if draft_needs else "None detected"
    bullets = "\n".join([f"- {note}" for note in risk_notes])

    return f"""## Evaluation Report

### Source Need Categories
{source_need_text}

### Draft Need Categories
{draft_need_text}

### Source Urgency Signal
{urgency}

### Lightweight Alignment Score
**{score}/5**

### Review Notes
{bullets}

### Human Reviewer Reminder
This evaluator is a lightweight QA support tool. A trained human should still compare the draft against the original note before use.
"""
