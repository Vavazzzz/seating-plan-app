from infrastructure.api.config import (
    SEAT_ENDPOINT,
    SEGMENTS_ENDPOINT,
    FEATURE_ENDPOINT
)

from infrastructure.api.apicaller import APICaller

def fetch_config_data(
    caller: APICaller, config_id: str
) -> tuple[dict, list | dict, dict]:
    seats_raw = caller.call_api(SEAT_ENDPOINT.format(config_id=config_id))
    segments_raw = caller.call_api(SEGMENTS_ENDPOINT.format(config_id=config_id))
    features_raw = caller.call_api(FEATURE_ENDPOINT.format(config_id=config_id))
    return seats_raw, segments_raw, features_raw