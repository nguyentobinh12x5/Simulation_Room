import json

from physics import RoomState
from publisher import (CMD_HVAC, CMD_OCCUPANCY, CMD_SETPOINT, CMD_TIMESCALE,
                       handle_command, make_payload)


def test_make_payload_matches_spec_format():
    p = json.loads(make_payload("temperature", 24.7, "C", "2026-07-16T20:14:03Z"))
    assert p == {"sensor": "temperature", "value": 24.7, "unit": "C",
                 "timestamp": "2026-07-16T20:14:03Z"}


def test_make_payload_default_timestamp_is_utc_iso_z():
    p = json.loads(make_payload("humidity", 45.2, "%"))
    assert p["timestamp"].endswith("Z") and "T" in p["timestamp"]


def test_hvac_command_on_off():
    s = RoomState(hvac_on=False)
    s2 = handle_command(s, CMD_HVAC, b'{"command": "on"}')
    assert s2.hvac_on is True
    s3 = handle_command(s2, CMD_HVAC, b'{"command": "off"}')
    assert s3.hvac_on is False


def test_occupancy_override_clamped():
    s = handle_command(RoomState(), CMD_OCCUPANCY, b'{"value": 8}')
    assert s.occupancy == 8
    s = handle_command(RoomState(), CMD_OCCUPANCY, b'{"value": 99}')
    assert s.occupancy == 30  # updated max


def test_malformed_command_is_ignored():
    s = RoomState(hvac_on=True)
    assert handle_command(s, CMD_HVAC, b"not json").hvac_on is True
    assert handle_command(s, CMD_HVAC, b'{"command": "banana"}').hvac_on is True


def test_non_object_json_command_is_ignored():
    s = RoomState(hvac_on=True, occupancy=5)
    assert handle_command(s, CMD_HVAC, b"null").hvac_on is True
    assert handle_command(s, CMD_HVAC, b"5").hvac_on is True
    assert handle_command(s, CMD_HVAC, b'"on"').hvac_on is True
    assert handle_command(s, CMD_OCCUPANCY, b"[1, 2]").occupancy == 5


def test_occupancy_bool_value_is_rejected():
    s = RoomState(occupancy=5)
    result = handle_command(s, CMD_OCCUPANCY, b'{"value": true}')
    assert result.occupancy == 5


# ─── New command tests ───────────────────────────────────

def test_setpoint_command():
    s = RoomState(setpoint=25.0)
    s2 = handle_command(s, CMD_SETPOINT, b'{"value": 22.5}')
    assert s2.setpoint == 22.5


def test_setpoint_command_clamped():
    s = RoomState()
    s2 = handle_command(s, CMD_SETPOINT, b'{"value": 10.0}')
    assert s2.setpoint == 18.0  # clamped to min
    s3 = handle_command(s, CMD_SETPOINT, b'{"value": 35.0}')
    assert s3.setpoint == 30.0  # clamped to max


def test_setpoint_bool_rejected():
    s = RoomState(setpoint=25.0)
    assert handle_command(s, CMD_SETPOINT, b'{"value": true}').setpoint == 25.0


def test_timescale_command():
    s = RoomState(time_scale=1.0)
    s2 = handle_command(s, CMD_TIMESCALE, b'{"value": 5}')
    assert s2.time_scale == 5.0


def test_timescale_invalid_value_rejected():
    s = RoomState(time_scale=1.0)
    # Value 3 is not in valid set {1, 2, 5, 10}
    s2 = handle_command(s, CMD_TIMESCALE, b'{"value": 3}')
    assert s2.time_scale == 1.0  # unchanged


def test_timescale_bool_rejected():
    s = RoomState(time_scale=1.0)
    assert handle_command(s, CMD_TIMESCALE, b'{"value": true}').time_scale == 1.0
