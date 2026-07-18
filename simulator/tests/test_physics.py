import random

from physics import (RoomState, auto_hvac_decision, clamp, step_humidity,
                     step_occupancy, step_temperature)


def run_temp(state, seconds):
    t = state.temperature
    for _ in range(seconds):
        t = step_temperature(
            RoomState(temperature=t, humidity=state.humidity,
                      occupancy=state.occupancy, hvac_on=state.hvac_on,
                      ac_power_pct=state.ac_power_pct),
            dt=1.0,
        )
    return t


def test_temp_rises_with_full_room():
    """With 8 people and AC off, temperature should rise noticeably in 15s."""
    t_after = run_temp(RoomState(temperature=24.0, occupancy=8, hvac_on=False), 15)
    assert t_after > 24.3  # temperature must rise


def test_temp_rises_faster_with_30_people():
    """With 30 people, temperature should rise much faster than with 8."""
    t_8 = run_temp(RoomState(temperature=24.0, occupancy=8, hvac_on=False), 15)
    t_30 = run_temp(RoomState(temperature=24.0, occupancy=30, hvac_on=False), 15)
    assert t_30 > t_8  # 30 people heats room faster


def test_temp_drops_with_ac_full_power():
    """AC at full power (100%) should cool effectively even with some occupants."""
    t_after = run_temp(
        RoomState(temperature=31.0, occupancy=3, hvac_on=True, ac_power_pct=1.0), 90
    )
    assert 31.0 - t_after >= 2.5


def test_ac_half_power_cools_slower():
    """AC at 50% power should cool slower than at 100%."""
    t_full = run_temp(
        RoomState(temperature=31.0, occupancy=3, hvac_on=True, ac_power_pct=1.0), 60
    )
    t_half = run_temp(
        RoomState(temperature=31.0, occupancy=3, hvac_on=True, ac_power_pct=0.5), 60
    )
    assert t_full < t_half  # full power cools more


def test_ac_zero_power_no_cooling():
    """AC on but 0% power should behave like AC off."""
    t_on_zero = run_temp(
        RoomState(temperature=26.0, occupancy=4, hvac_on=True, ac_power_pct=0.0), 30
    )
    t_off = run_temp(
        RoomState(temperature=26.0, occupancy=4, hvac_on=False), 30
    )
    assert abs(t_on_zero - t_off) < 0.01


def test_hvac_flag_changes_direction_immediately():
    base = RoomState(temperature=26.0, occupancy=4, hvac_on=False)
    up = step_temperature(base, dt=1.0)
    down = step_temperature(
        RoomState(temperature=26.0, occupancy=4, hvac_on=True, ac_power_pct=1.0),
        dt=1.0,
    )
    assert up > 26.0 and down < 26.0


def test_humidity_rises_with_people_and_clamps():
    s = RoomState(humidity=45.0, occupancy=6, hvac_on=False)
    assert step_humidity(s, dt=5.0) > 45.0
    high = RoomState(humidity=80.0, occupancy=10, hvac_on=False)
    assert step_humidity(high, dt=5.0) == 80.0  # ceiling clamp
    dry = RoomState(humidity=15.0, occupancy=0, hvac_on=True, ac_power_pct=1.0)
    assert step_humidity(dry, dt=5.0) == 15.0  # floor clamp


def test_humidity_ac_dries_proportional_to_power():
    """AC at 50% power should dry less than at 100%."""
    full = step_humidity(
        RoomState(humidity=60.0, occupancy=2, hvac_on=True, ac_power_pct=1.0), dt=10.0
    )
    half = step_humidity(
        RoomState(humidity=60.0, occupancy=2, hvac_on=True, ac_power_pct=0.5), dt=10.0
    )
    assert full < half  # full power dries more


def test_occupancy_random_walk_stays_in_bounds():
    rng = random.Random(42)
    occ = 5
    seen = set()
    for _ in range(500):
        s = RoomState(occupancy=occ)
        occ = step_occupancy(s, rng)
        seen.add(occ)
        assert 0 <= occ <= 30  # updated max
    assert len(seen) > 1  # has variation


def test_occupancy_high_count_wider_walk():
    """At high occupancy (>20), step_occupancy should allow wider deltas."""
    rng = random.Random(42)
    deltas = set()
    for _ in range(200):
        s = RoomState(occupancy=25)
        new_occ = step_occupancy(s, rng)
        deltas.add(new_occ - 25)
    # Should see deltas beyond ±1
    assert max(deltas) > 1 or min(deltas) < -1


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(99, 0, 10) == 10


def test_auto_off_when_room_empty():
    # No occupants -> always off, even if the room is hot
    assert auto_hvac_decision(35.0, 24.0, 0, currently_on=True) is False


def test_auto_engages_when_warm_and_occupied():
    # Occupied and above target -> AC turns on
    assert auto_hvac_decision(24.5, 24.0, 5, currently_on=False) is True


def test_auto_stays_on_while_occupied_at_target():
    # Occupied, cooled to/below target -> stays on (PID modulates power, no off)
    assert auto_hvac_decision(23.5, 24.0, 5, currently_on=True) is True


def test_auto_stays_off_when_occupied_but_cool():
    # Occupied but not yet above target and currently off -> holds off
    assert auto_hvac_decision(23.5, 24.0, 5, currently_on=False) is False
