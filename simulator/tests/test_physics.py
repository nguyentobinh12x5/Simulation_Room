import random

from physics import RoomState, clamp, step_humidity, step_occupancy, step_temperature


def run_temp(state, seconds):
    t = state.temperature
    for _ in range(seconds):
        t = step_temperature(
            RoomState(temperature=t, humidity=state.humidity,
                      occupancy=state.occupancy, hvac_on=state.hvac_on),
            dt=1.0,
        )
    return t


def test_temp_rises_03_to_05_per_15s_when_full_room():
    # Mục tiêu spec: occupancy=8, AC off -> tăng 0.3-0.5°C mỗi 15s
    t_after = run_temp(RoomState(temperature=24.0, occupancy=8, hvac_on=False), 15)
    assert 0.3 <= t_after - 24.0 <= 0.5


def test_temp_drops_at_least_25_within_90s_when_ac_on():
    # Mục tiêu spec: bật AC -> về bình thường trong ~60-90s
    t_after = run_temp(RoomState(temperature=31.0, occupancy=3, hvac_on=True), 90)
    assert 31.0 - t_after >= 2.5


def test_hvac_flag_changes_direction_immediately():
    base = RoomState(temperature=26.0, occupancy=4, hvac_on=False)
    up = step_temperature(base, dt=1.0)
    down = step_temperature(RoomState(temperature=26.0, occupancy=4, hvac_on=True), dt=1.0)
    assert up > 26.0 and down < 26.0


def test_humidity_rises_with_people_and_clamps():
    s = RoomState(humidity=45.0, occupancy=6, hvac_on=False)
    assert step_humidity(s, dt=5.0) > 45.0
    high = RoomState(humidity=80.0, occupancy=10, hvac_on=False)
    assert step_humidity(high, dt=5.0) == 80.0  # clamp trần
    dry = RoomState(humidity=15.0, occupancy=0, hvac_on=True)
    assert step_humidity(dry, dt=5.0) == 15.0  # clamp sàn


def test_occupancy_random_walk_stays_in_bounds():
    rng = random.Random(42)
    occ = 5
    seen = set()
    for _ in range(500):
        s = RoomState(occupancy=occ)
        occ = step_occupancy(s, rng)
        seen.add(occ)
        assert 0 <= occ <= 10
    assert len(seen) > 1  # có biến thiên, không đứng yên


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(99, 0, 10) == 10
