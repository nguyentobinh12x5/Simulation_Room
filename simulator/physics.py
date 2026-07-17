"""Physics model for the lab room. Constants are locked by tests/test_physics.py."""
import random
from dataclasses import dataclass

HEAT_PER_PERSON_W = 100.0     # each person emits ~100W of heat
WALL_K = 0.05                 # heat transfer through walls (W/°C)
AC_POWER_W = 3500.0           # max cooling power of AC (variable-speed)
ROOM_HEAT_CAPACITY = 25000.0  # J/°C
T_OUTDOOR = 32.0
HUMIDITY_PER_PERSON = 0.06    # %/s per person
AC_DRY_RATE = 0.5             # max %/s dehumidification when AC at full power

TEMP_MIN, TEMP_MAX = 15.0, 40.0
HUM_MIN, HUM_MAX = 15.0, 80.0
OCC_MIN, OCC_MAX = 0, 30

# AC output temperature mapping: power% -> output air temperature
AC_TEMP_MAX = 28.0   # output temp at 0% power (just fan, no cooling)
AC_TEMP_MIN = 16.0   # output temp at 100% power (max cooling)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


@dataclass
class RoomState:
    temperature: float = 24.0
    humidity: float = 45.0
    occupancy: int = 2
    hvac_on: bool = False
    ac_power_pct: float = 0.0    # 0.0 - 1.0 (0% - 100% of max AC power)
    setpoint: float = 25.0       # desired room temperature (°C)
    time_scale: float = 1.0      # simulation speed multiplier


def ac_output_temperature(power_pct: float) -> float:
    """Calculate the AC output air temperature based on power percentage.

    At 0% power: 28°C (just fan, no cooling)
    At 100% power: 16°C (max cooling)
    """
    pct = clamp(power_pct, 0.0, 1.0)
    return AC_TEMP_MAX - (AC_TEMP_MAX - AC_TEMP_MIN) * pct


def step_temperature(state: RoomState, dt: float) -> float:
    """Advance room temperature by dt seconds.

    Heat sources: people + outdoor heat transfer
    Heat sink: AC cooling (proportional to ac_power_pct when hvac_on)
    """
    q_people = state.occupancy * HEAT_PER_PERSON_W
    q_outdoor = WALL_K * (T_OUTDOOR - state.temperature)
    q_ac = -AC_POWER_W * state.ac_power_pct if state.hvac_on else 0.0
    t_next = state.temperature + (dt / ROOM_HEAT_CAPACITY) * (q_people + q_outdoor + q_ac)
    return clamp(t_next, TEMP_MIN, TEMP_MAX)


def step_humidity(state: RoomState, dt: float) -> float:
    """Advance room humidity by dt seconds.

    Humidity rises with people, falls with AC (proportional to power).
    """
    ac_dry = AC_DRY_RATE * state.ac_power_pct if state.hvac_on else 0.0
    rate = state.occupancy * HUMIDITY_PER_PERSON - ac_dry
    return clamp(state.humidity + rate * dt, HUM_MIN, HUM_MAX)


def step_occupancy(state: RoomState, rng: random.Random) -> int:
    """Random walk for occupancy, with wider steps at higher counts.

    At low occupancy (< 10): ±1 steps, biased toward staying
    At medium occupancy (10-20): ±1 to ±2 steps
    At high occupancy (> 20): ±1 to ±3 steps
    """
    if state.occupancy > 20:
        delta = rng.choice([-3, -2, -1, 0, 0, 1, 2, 3])
    elif state.occupancy > 10:
        delta = rng.choice([-2, -1, 0, 0, 1, 2])
    else:
        delta = rng.choice([-1, 0, 0, 1])  # biased toward staying still
    return clamp(state.occupancy + delta, OCC_MIN, OCC_MAX)
