"""Maps API importer for seating plans."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.models.seating_plan import SeatingPlan

from domain.exceptions import SeatingPlanException
from domain.utils.alphanum_handler import alphanum_sort_key
from .abstract import Importer


class APIImporter(Importer):
    """Import seating plans from Maps API responses.

    Unlike file-based importers, the "source" is the tuple returned by
    ``fetch_config_data``: ``(seats_raw, segments_raw, features_raw)``.
    Only the first two elements are used.
    """

    def supports(self, api_response: tuple | list) -> bool:
        """Check that the response looks like (seats, segments, ...)."""
        return isinstance(api_response, (tuple, list)) and len(api_response) >= 2

    def import_seating_plan(
        self, api_response: tuple | list, plan_name: str | None = None
    ) -> "SeatingPlan":
        """Import a seating plan from raw API data.

        Args:
            api_response: (seats_raw, segments_raw, ...) as returned by fetch_config_data
            plan_name: Name for the imported seating plan

        Returns:
            A populated SeatingPlan instance

        Raises:
            SeatingPlanException: If the data is malformed or import fails
        """
        try:
            from domain.models.seating_plan import SeatingPlan

            if not self.supports(api_response):
                raise SeatingPlanException(
                    "Expected a (seats, segments) API response",
                    error_code="INVALID_API_RESPONSE",
                )

            seats_raw, segments_raw = api_response[0], api_response[1]
            seat_features = self._extract_seat_features(seats_raw)
            if not isinstance(segments_raw, list):
                raise SeatingPlanException(
                    "Segments payload must be a list",
                    error_code="INVALID_API_RESPONSE",
                )

            seating_plan = SeatingPlan(plan_name or "Imported Plan")
            sid_to_name = self._build_sections(seating_plan, segments_raw)
            self._add_seats(seating_plan, sid_to_name, seat_features)
            return seating_plan

        except SeatingPlanException:
            raise
        except Exception as e:
            raise SeatingPlanException(
                f"Failed to import API data: {e}",
                error_code="IMPORT_FAILED",
            ) from e

    # ---- Helpers ----
    @staticmethod
    def _extract_seat_features(seats_raw: dict) -> list[dict]:
        if not isinstance(seats_raw, dict) or not isinstance(seats_raw.get("features"), list):
            raise SeatingPlanException(
                "Seat payload must be a GeoJSON FeatureCollection",
                error_code="INVALID_API_RESPONSE",
            )
        return seats_raw["features"]

    @staticmethod
    def _build_sections(seating_plan: "SeatingPlan", segments: list[dict]) -> dict[str, str]:
        """Create sections in segment order; return a map of sid -> section name.

        The section name comes from the SECTION child segment (id "s_24:HASH"),
        falling back to the COMPOSITE name when there is none (e.g. GA areas).
        """
        section_names = {
            seg["id"].split(":", 1)[0]: seg["name"]
            for seg in segments
            if seg.get("segmentCategory") == "SECTION"
        }

        sid_to_name: dict[str, str] = {}
        for seg in segments:
            if seg.get("segmentCategory") != "COMPOSITE":
                continue
            sid = seg["id"]
            name = (section_names.get(sid) or seg.get("name") or "").strip()
            if not name:
                continue
            seating_plan.add_section(name, is_ga=bool(seg.get("generalAdmission", False)))
            sid_to_name[sid] = name
        return sid_to_name

    @staticmethod
    def _add_seats(
        seating_plan: "SeatingPlan",
        sid_to_name: dict[str, str],
        seat_features: list[dict],
    ) -> None:
        """Group seats per section, sort naturally, then add them."""
        seats_by_section: dict[str, set[tuple[str, str]]] = {}
        for feature in seat_features:
            props = feature.get("properties") or {}
            name = sid_to_name.get(props.get("sid"))
            row = str(props.get("r", "")).strip()
            number = str(props.get("n", "")).strip()
            if name is None or not row or not number:
                continue
            seats_by_section.setdefault(name, set()).add((row, number))

        for name, seats in seats_by_section.items():
            section = seating_plan.sections[name]
            if section.is_ga:
                continue
            ordered = sorted(
                seats, key=lambda s: (alphanum_sort_key(s[0]), alphanum_sort_key(s[1]))
            )
            for row, number in ordered:
                section.add_seat(row, number)
