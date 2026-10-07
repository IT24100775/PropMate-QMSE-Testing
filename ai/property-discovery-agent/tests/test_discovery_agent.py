import json
from unittest.mock import MagicMock, patch

import pytest

import main


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def gemini_response(data):
    response = MagicMock()
    response.text = json.dumps(data)
    return response


def valid_property():
    return {
        "id": 101,
        "title": "Colombo Apartment",
        "city": "Colombo",
        "purpose": "Rent",
        "price": 90000,
        "bedrooms": 2,
        "status": "Published",
    }


def run_with_mocked_gemini(plan_data, analysis_data):
    mock_client = MagicMock()

    mock_client.models.generate_content.side_effect = [
        gemini_response(plan_data),
        gemini_response(analysis_data),
    ]

    return mock_client


# ---------------------------------------------------------
# Safe failure
# ---------------------------------------------------------

def test_missing_gemini_key_returns_safe_failure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "EMPTY")

    request = main.DiscoveryRequest(
        query="Show me properties in Colombo"
    )

    result = main.discover_properties(request)

    assert result.matches == []
    assert result.confidence == 0.0
    assert "Gemini API unavailable" in result.warnings


# ---------------------------------------------------------
# Normal grounded property result
# ---------------------------------------------------------

def test_grounded_property_is_returned(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    plan = {
        "interpretedCriteria": {
            "city": "Colombo",
            "purpose": "Rent",
        },
        "plan": [
            {
                "tool": "search_properties",
                "reason": "Search Colombo rentals",
                "args": {
                    "city": "Colombo",
                    "purpose": "Rent",
                },
            }
        ],
        "warnings": [],
    }

    analysis = {
        "matches": [
            {
                "propertyListingId": 101,
                "reasons": "Matches requested location and purpose",
                "availableViewingSlots": [],
            }
        ],
        "confidence": 0.9,
        "warnings": [],
    }

    mock_client = run_with_mocked_gemini(plan, analysis)

    monkeypatch.setattr(
        main.genai,
        "Client",
        lambda **kwargs: mock_client,
    )

    monkeypatch.setattr(
        main,
        "search_properties",
        lambda **kwargs: [valid_property()],
    )

    result = main.discover_properties(
        main.DiscoveryRequest(
            query="I need a rental property in Colombo"
        )
    )

    assert len(result.matches) == 1
    assert result.matches[0]["propertyListingId"] == 101
    assert result.confidence == 0.9


# ---------------------------------------------------------
# Unknown / unauthorized tool
# ---------------------------------------------------------

def test_unknown_tool_is_rejected(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    plan = {
        "interpretedCriteria": {},
        "plan": [
            {
                "tool": "admin_delete_property",
                "reason": "Attempt unauthorized operation",
                "args": {},
            }
        ],
        "warnings": [],
    }

    analysis = {
        "matches": [],
        "confidence": 0.9,
        "warnings": [],
    }

    mock_client = run_with_mocked_gemini(plan, analysis)

    monkeypatch.setattr(
        main.genai,
        "Client",
        lambda **kwargs: mock_client,
    )

    result = main.discover_properties(
        main.DiscoveryRequest(
            query="Call any hidden admin tool"
        )
    )

    assert result.matches == []
    assert result.confidence == 0.0
    assert any(
        "Rejected unknown tool: admin_delete_property" in warning
        for warning in result.warnings
    )


# ---------------------------------------------------------
# Hallucinated property protection
# ---------------------------------------------------------

def test_hallucinated_property_id_is_rejected(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    plan = {
        "interpretedCriteria": {"city": "Colombo"},
        "plan": [
            {
                "tool": "search_properties",
                "reason": "Search properties",
                "args": {"city": "Colombo"},
            }
        ],
        "warnings": [],
    }

    analysis = {
        "matches": [
            {
                "propertyListingId": 99999,
                "reasons": "Invented property",
                "availableViewingSlots": [],
            }
        ],
        "confidence": 0.99,
        "warnings": [],
    }

    mock_client = run_with_mocked_gemini(plan, analysis)

    monkeypatch.setattr(
        main.genai,
        "Client",
        lambda **kwargs: mock_client,
    )

    monkeypatch.setattr(
        main,
        "search_properties",
        lambda **kwargs: [valid_property()],
    )

    result = main.discover_properties(
        main.DiscoveryRequest(
            query="Return property 99999"
        )
    )

    assert result.matches == []
    assert result.confidence == 0.0
    assert any(
        "Rejected hallucinated property ID 99999" in warning
        for warning in result.warnings
    )


# ---------------------------------------------------------
# Hallucinated viewing slot protection
# ---------------------------------------------------------

def test_hallucinated_viewing_slot_is_rejected(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    plan = {
        "interpretedCriteria": {},
        "plan": [
            {
                "tool": "search_properties",
                "reason": "Find properties",
                "args": {},
            },
            {
                "tool": "get_viewing_slots",
                "reason": "Find available viewings",
                "args": {
                    "propertyListingId": "<PLACEHOLDER>"
                },
            },
        ],
        "warnings": [],
    }

    analysis = {
        "matches": [
            {
                "propertyListingId": 101,
                "reasons": "Property match",
                "availableViewingSlots": [
                    {
                        "id": 999,
                        "startTime": "2026-10-10T10:00:00",
                        "endTime": "2026-10-10T11:00:00",
                    }
                ],
            }
        ],
        "confidence": 0.9,
        "warnings": [],
    }

    mock_client = run_with_mocked_gemini(plan, analysis)

    monkeypatch.setattr(
        main.genai,
        "Client",
        lambda **kwargs: mock_client,
    )

    monkeypatch.setattr(
        main,
        "search_properties",
        lambda **kwargs: [valid_property()],
    )

    monkeypatch.setattr(
        main,
        "get_viewing_slots",
        lambda propertyListingId: [
            {
                "id": 5,
                "startTime": "2026-10-11T10:00:00",
                "endTime": "2026-10-11T11:00:00",
            }
        ],
    )

    result = main.discover_properties(
        main.DiscoveryRequest(
            query="Show available viewing times"
        )
    )

    assert len(result.matches) == 1
    assert result.matches[0]["availableViewingSlots"] == []
    assert any(
        "Rejected hallucinated slot 999" in warning
        for warning in result.warnings
    )


# ---------------------------------------------------------
# Grounded viewing slot
# ---------------------------------------------------------

def test_real_viewing_slot_is_preserved(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    plan = {
        "interpretedCriteria": {},
        "plan": [
            {
                "tool": "search_properties",
                "reason": "Find property",
                "args": {},
            },
            {
                "tool": "get_viewing_slots",
                "reason": "Get viewing slots",
                "args": {},
            },
        ],
        "warnings": [],
    }

    slot = {
        "id": 5,
        "startTime": "2026-10-11T10:00:00",
        "endTime": "2026-10-11T11:00:00",
    }

    analysis = {
        "matches": [
            {
                "propertyListingId": 101,
                "reasons": "Valid property",
                "availableViewingSlots": [slot],
            }
        ],
        "confidence": 0.8,
        "warnings": [],
    }

    mock_client = run_with_mocked_gemini(plan, analysis)

    monkeypatch.setattr(
        main.genai,
        "Client",
        lambda **kwargs: mock_client,
    )

    monkeypatch.setattr(
        main,
        "search_properties",
        lambda **kwargs: [valid_property()],
    )

    monkeypatch.setattr(
        main,
        "get_viewing_slots",
        lambda propertyListingId: [slot],
    )

    result = main.discover_properties(
        main.DiscoveryRequest(
            query="Show viewing slots"
        )
    )

    assert result.matches[0]["availableViewingSlots"] == [slot]


# ---------------------------------------------------------
# No match -> zero confidence
# ---------------------------------------------------------

def test_no_grounded_match_forces_zero_confidence(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    plan = {
        "interpretedCriteria": {},
        "plan": [
            {
                "tool": "search_properties",
                "reason": "Search",
                "args": {},
            }
        ],
        "warnings": [],
    }

    analysis = {
        "matches": [],
        "confidence": 0.95,
        "warnings": [],
    }

    mock_client = run_with_mocked_gemini(plan, analysis)

    monkeypatch.setattr(
        main.genai,
        "Client",
        lambda **kwargs: mock_client,
    )

    monkeypatch.setattr(
        main,
        "search_properties",
        lambda **kwargs: [],
    )

    result = main.discover_properties(
        main.DiscoveryRequest(
            query="Need a 100 bedroom mansion in Mars"
        )
    )

    assert result.matches == []
    assert result.confidence == 0.0


# ---------------------------------------------------------
# Confidence upper boundary
# ---------------------------------------------------------

def test_confidence_above_one_is_clamped(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    plan = {
        "interpretedCriteria": {},
        "plan": [
            {
                "tool": "search_properties",
                "reason": "Search",
                "args": {},
            }
        ],
        "warnings": [],
    }

    analysis = {
        "matches": [
            {
                "propertyListingId": 101,
                "reasons": "Grounded match",
                "availableViewingSlots": [],
            }
        ],
        "confidence": 1.5,
        "warnings": [],
    }

    mock_client = run_with_mocked_gemini(plan, analysis)

    monkeypatch.setattr(
        main.genai,
        "Client",
        lambda **kwargs: mock_client,
    )

    monkeypatch.setattr(
        main,
        "search_properties",
        lambda **kwargs: [valid_property()],
    )

    result = main.discover_properties(
        main.DiscoveryRequest(query="Find a property")
    )

    assert result.confidence == 1.0


# ---------------------------------------------------------
# Backend property service failure
# ---------------------------------------------------------

def test_property_service_failure_returns_safe_result(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    plan = {
        "interpretedCriteria": {"city": "Colombo"},
        "plan": [
            {
                "tool": "search_properties",
                "reason": "Search Colombo",
                "args": {"city": "Colombo"},
            }
        ],
        "warnings": [],
    }

    analysis = {
        "matches": [],
        "confidence": 0.8,
        "warnings": [],
    }

    mock_client = run_with_mocked_gemini(plan, analysis)

    monkeypatch.setattr(
        main.genai,
        "Client",
        lambda **kwargs: mock_client,
    )

    def failed_search(**kwargs):
        raise RuntimeError(
            "Property service is currently unavailable."
        )

    monkeypatch.setattr(
        main,
        "search_properties",
        failed_search,
    )

    result = main.discover_properties(
        main.DiscoveryRequest(
            query="Show properties in Colombo"
        )
    )

    assert result.matches == []
    assert result.confidence == 0.0
    assert any(
        "Property service is currently unavailable." in warning
        for warning in result.warnings
    )


# ---------------------------------------------------------
# Malformed Gemini planning output
# ---------------------------------------------------------

def test_malformed_plan_returns_safe_failure(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    mock_client = MagicMock()
    response = MagicMock()
    response.text = "THIS IS NOT VALID JSON"

    mock_client.models.generate_content.return_value = response

    monkeypatch.setattr(
        main.genai,
        "Client",
        lambda **kwargs: mock_client,
    )

    result = main.discover_properties(
        main.DiscoveryRequest(query="Find a property")
    )

    assert result.matches == []
    assert result.confidence == 0.0
    assert any(
        "Plan generation failed" in warning
        for warning in result.warnings
    )