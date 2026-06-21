from src.triage_engine import analyze_note


def test_housing_urgency_detected():
    note = "Client received an eviction notice and may need to leave apartment next week."
    result = analyze_note(note)
    assert "housing" in result.need_categories
    assert "High" in result.urgency


def test_employment_detected():
    note = "Client wants help with a resume and interview preparation after losing a job."
    result = analyze_note(note)
    assert "employment" in result.need_categories


def test_missing_info_present():
    note = "Client asked about nearby food pantry resources."
    result = analyze_note(note)
    assert len(result.missing_information) > 0
