"""Tests for SeatingPlanService.import_from_api (no network, no PyQt6)."""

import pytest

from application.handlers import CommandHandler
from application.services import SeatingPlanService
from domain.exceptions import SeatingPlanException
from domain.models.seating_plan import SeatingPlan
from infrastructure.import_export import APIImporter


SEATS = {
    "type": "FeatureCollection",
    "features": [
        {"properties": {"sid": "s_1", "r": "2", "n": "10"}},
        {"properties": {"sid": "s_1", "r": "1", "n": "2"}},
        {"properties": {"sid": "s_1", "r": "1", "n": "1"}},
        {"properties": {"sid": "s_1", "r": "", "n": "5"}},      # skipped: no row
        {"properties": {"sid": "s_unknown", "r": "1", "n": "1"}},  # skipped: no section
    ],
}
SEGMENTS = [
    {"id": "s_1", "name": "SECTION A", "segmentCategory": "COMPOSITE"},
    {"id": "s_1:HASH", "name": "Section A", "segmentCategory": "SECTION"},
    {"id": "s_2", "name": "PIT", "segmentCategory": "COMPOSITE", "generalAdmission": True},
]


def make_service(fetch=None, importer=None, configured=True):
    plan = SeatingPlan("Untitled")
    plan.add_section("Old")
    config = {}
    if configured:
        config = {
            "api_fetch": fetch or (lambda cid: (SEATS, SEGMENTS, {})),
            "api_importer": importer or APIImporter(),
        }
    return SeatingPlanService(plan, CommandHandler(), config), plan


def test_success_replaces_plan_and_names_it():
    service, plan = make_service()
    result = service.import_from_api("123", "My Plan")
    assert result.is_success()
    assert plan.name == "My Plan"
    assert list(plan.sections) == ["Section A", "PIT"]  # SECTION name, segment order
    assert plan.sections["PIT"].is_ga
    assert list(plan.sections["Section A"].seats) == ["1-1", "1-2", "2-10"]


def test_default_plan_name():
    service, plan = make_service()
    assert service.import_from_api("123").is_success()
    assert plan.name == "Config 123"


@pytest.mark.parametrize("bad_id", ["", "   ", "abc", "12a", "-5"])
def test_invalid_config_id_leaves_plan_untouched(bad_id):
    service, plan = make_service()
    result = service.import_from_api(bad_id)
    assert not result.is_success()
    assert list(plan.sections) == ["Old"]


def test_fetch_failure_returns_failure():
    def fetch(cid):
        raise SeatingPlanException("boom", error_code="API_REQUEST_FAILED")

    service, plan = make_service(fetch=fetch)
    result = service.import_from_api("123")
    assert not result.is_success()
    assert list(plan.sections) == ["Old"]


def test_malformed_payload_returns_failure():
    service, plan = make_service(fetch=lambda cid: ({"nope": 1}, SEGMENTS, {}))
    assert not service.import_from_api("123").is_success()
    assert list(plan.sections) == ["Old"]


def test_not_configured_returns_failure():
    service, _ = make_service(configured=False)
    assert not service.import_from_api("123").is_success()
