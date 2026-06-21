from dataclasses import dataclass, asdict
from typing import Dict, List
import re


NEED_KEYWORDS: Dict[str, List[str]] = {
    "housing": ["rent", "eviction", "shelter", "housing", "homeless", "landlord", "lease", "utility", "utilities"],
    "food": ["food", "meal", "groceries", "pantry", "snap", "hungry"],
    "employment": ["job", "employment", "resume", "interview", "laid off", "unemployed", "work", "career"],
    "education": ["school", "class", "student", "college", "training", "certificate", "ged", "course"],
    "transportation": ["bus", "transportation", "car", "ride", "gas", "commute", "transit"],
    "health": ["health", "medical", "doctor", "medication", "clinic", "therapy", "insurance"],
    "legal": ["legal", "court", "lawyer", "immigration", "tenant rights", "documentation"],
    "childcare": ["childcare", "child care", "children", "kids", "daycare", "school pickup"],
    "financial": ["debt", "bill", "bills", "income", "financial", "cash", "bank", "benefits"]
}

URGENT_KEYWORDS = [
    "eviction notice", "evicted", "homeless", "unsafe", "no food", "without food",
    "domestic violence", "violence", "suicidal", "self-harm", "medical emergency",
    "crisis", "court date", "shutoff", "shut off"
]

MISSING_INFO_PROMPTS = {
    "housing": ["Current housing status", "Deadline or eviction date", "Monthly rent or amount owed"],
    "food": ["Household size", "Immediate food access", "Eligibility for food assistance"],
    "employment": ["Current work status", "Resume status", "Target roles or training interests"],
    "education": ["Current program or grade level", "Schedule constraints", "Needed academic support"],
    "transportation": ["Primary transportation method", "Route or commute barrier", "Timing of need"],
    "health": ["Whether urgent care is needed", "Insurance or clinic access", "Medication continuity concerns"],
    "legal": ["Deadline or court date", "Type of legal issue", "Existing representation"],
    "childcare": ["Age of children", "Schedule needed", "Care location constraints"],
    "financial": ["Income source", "Amount owed", "Immediate payment deadlines"]
}


@dataclass
class IntakeAnalysis:
    summary: str
    need_categories: List[str]
    urgency: str
    urgency_reasons: List[str]
    suggested_next_steps: List[str]
    missing_information: List[str]
    evidence_snippets: List[str]
    human_review_checklist: List[str]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def sentence_split(text: str) -> List[str]:
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in raw if s.strip()]


def find_evidence(text: str, keywords: List[str], limit: int = 4) -> List[str]:
    sentences = sentence_split(text)
    found = []
    lower_keywords = [k.lower() for k in keywords]
    for sentence in sentences:
        s_lower = sentence.lower()
        if any(k in s_lower for k in lower_keywords):
            found.append(sentence)
        if len(found) >= limit:
            break
    return found


def detect_needs(text: str) -> List[str]:
    text_l = normalize(text)
    categories = []
    for category, keywords in NEED_KEYWORDS.items():
        if any(keyword in text_l for keyword in keywords):
            categories.append(category)
    return categories


def detect_urgency(text: str) -> tuple[str, List[str]]:
    text_l = normalize(text)
    matches = [kw for kw in URGENT_KEYWORDS if kw in text_l]
    if matches:
        return "High: human review recommended soon", matches
    if any(word in text_l for word in ["soon", "deadline", "urgent", "this week", "tomorrow"]):
        return "Medium: time-sensitive follow-up likely", ["time-sensitive language"]
    return "Routine: no explicit urgent risk detected", []


def build_summary(text: str, needs: List[str], urgency: str) -> str:
    sentences = sentence_split(text)
    first_sentence = sentences[0] if sentences else "No source note provided."
    need_text = ", ".join(needs) if needs else "no clear need category detected"
    return f"The note appears to involve {need_text}. Key context: {first_sentence} Urgency assessment: {urgency}."


def build_next_steps(needs: List[str], urgency: str) -> List[str]:
    steps = []
    if "High" in urgency:
        steps.append("Route to a trained staff member for prompt review before sending any response.")
    for need in needs:
        if need == "housing":
            steps.append("Confirm housing timeline, amount owed, and whether an eviction or utility deadline exists.")
        elif need == "food":
            steps.append("Check immediate food access and provide pantry or benefits navigation resources if appropriate.")
        elif need == "employment":
            steps.append("Offer resume, job search, interview, or training-program support.")
        elif need == "education":
            steps.append("Clarify academic or training goals and identify next support touchpoint.")
        elif need == "transportation":
            steps.append("Confirm commute barrier and identify transit, ride, or gas-card resources if available.")
        elif need == "health":
            steps.append("Confirm whether medical needs are urgent and route to qualified staff or clinic resources.")
        elif need == "legal":
            steps.append("Avoid giving legal advice. Provide referral to qualified legal aid if applicable.")
        elif need == "childcare":
            steps.append("Confirm childcare schedule, child ages, and eligibility for local childcare resources.")
        elif need == "financial":
            steps.append("Clarify immediate payment deadlines and connect to benefits or financial coaching resources if available.")
    if not steps:
        steps.append("Ask a staff member to review the note and identify the appropriate program pathway.")
    steps.append("Document any follow-up action and mark unknown details as missing rather than guessing.")
    return steps


def build_missing_info(needs: List[str]) -> List[str]:
    missing = []
    for need in needs:
        missing.extend(MISSING_INFO_PROMPTS.get(need, []))
    if not missing:
        missing = ["Client goal", "Deadline or timeline", "Best follow-up channel", "Program eligibility context"]
    return list(dict.fromkeys(missing))


def analyze_note(text: str) -> IntakeAnalysis:
    needs = detect_needs(text)
    urgency, reasons = detect_urgency(text)
    summary = build_summary(text, needs, urgency)

    all_keywords = []
    for need in needs:
        all_keywords.extend(NEED_KEYWORDS.get(need, []))
    all_keywords.extend(URGENT_KEYWORDS)

    evidence = find_evidence(text, all_keywords) or sentence_split(text)[:2]

    checklist = [
        "Review source note before using the brief.",
        "Confirm all missing information with the client or staff member.",
        "Do not treat urgency flags as final determinations.",
        "Do not provide medical, legal, housing, or benefit decisions through this tool.",
        "Record final staff decision in the organization’s approved system."
    ]

    return IntakeAnalysis(
        summary=summary,
        need_categories=needs or ["Unclear"],
        urgency=urgency,
        urgency_reasons=reasons or ["No explicit urgent keywords found"],
        suggested_next_steps=build_next_steps(needs, urgency),
        missing_information=build_missing_info(needs),
        evidence_snippets=evidence,
        human_review_checklist=checklist
    )


def format_markdown_brief(analysis: IntakeAnalysis) -> str:
    data = asdict(analysis)

    def bullets(items):
        return "\n".join([f"- {item}" for item in items])

    return f"""## Intake Brief

### Summary
{data["summary"]}

### Need Categories
{bullets(data["need_categories"])}

### Urgency
{data["urgency"]}

**Reasons**
{bullets(data["urgency_reasons"])}

### Suggested Next Steps
{bullets(data["suggested_next_steps"])}

### Missing Information to Confirm
{bullets(data["missing_information"])}

### Source Evidence Snippets
{bullets(data["evidence_snippets"])}

### Human Review Checklist
{bullets(data["human_review_checklist"])}
"""
