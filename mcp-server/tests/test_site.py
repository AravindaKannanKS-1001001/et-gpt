"""Company knowledge retrieval keeps short facts (contacts) and gates confidence."""
from et_mcp.services.site import retrieval


def _top(query):
    evidence, confident = retrieval.search(query, 5)
    return evidence, confident


def test_contact_details_are_retrievable_and_confident():
    evidence, confident = _top("EarthTekniks email address")
    assert confident
    assert any("automation@earthtekniks.com" in e.text for e in evidence)


def test_office_location_is_found():
    evidence, confident = _top("where is the office located")
    assert confident and any("Maraimalai Nagar" in e.text for e in evidence)


def test_plural_and_brand_spelling():
    evidence, confident = _top("bottle inspection projects")
    assert confident and evidence[0].doc_id == "project_ampoule_bottle_inspection_system"


def test_unrelated_question_is_not_confident():
    evidence, confident = _top("who won the cricket world cup")
    assert not confident
