# Handoff Guide

This guide explains how another person could run, adapt, and maintain the MissionOps Intake Assistant.

## Setup

1. Install Python 3.10 or later.
2. Clone the repository.
3. Create a virtual environment.
4. Install requirements.
5. Run `streamlit run app.py`.

## Adapting need categories

Need categories live in `src/triage_engine.py` inside the `NEED_KEYWORDS` dictionary.

To add a category:

```python
"benefits": ["medicaid", "snap", "benefits", "application"]
```

## Adapting urgency flags

Urgency flags live in `URGENT_KEYWORDS`.

Organizations should review these keywords with trained staff. This prototype uses simple keyword matching and is not a final triage tool.

## Using Claude API mode

Set the environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

Then turn on "Use Claude API if available" in the sidebar.

## Review workflow

1. Staff member loads source note.
2. App generates structured brief.
3. Staff member compares brief with source.
4. Staff member confirms missing details.
5. Staff member records final action in approved system.

## Maintenance owner

Recommended owner: operations lead, program manager, or AI workflow lead.

## Known limitations

- Keyword matching is simple.
- Urgency detection is not comprehensive.
- No sensitive-data redaction yet.
- No authentication yet.
- No database yet.
