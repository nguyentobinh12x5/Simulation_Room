"""Mo hinh vat ly phong lab. Cac hang so duoc khoa boi tests/test_physics.py."""
import random
from dataclasses import dataclass

HEAT_PER_PERSON_W = 100.0     # moi nguoi toa ~100W
WALL_K = 0.05                 # truyen nhiet qua tuong (W/°C)
AC_POWER_W = 1500.0           # cong suat rut nhiet cua AC
ROOM_HEAT_CAPACITY = 25000.0  # J/°C
T_OUTDOOR = 32.0
HUMIDITY_PER_PERSON = 0.06    # %/s moi nguoi
AC_DRY_RATE = 0.5             # %/s khi AC bat

TEMP_MIN, TEMP_MAX = 15.0, 40.0
HUM_MIN, HUM_MAX = 15.0, 80.0
OCC_MIN, OCC_MAX = 0, 10


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


@dataclass
class RoomState:
    temperature: float = 24.0
    humidity: float = 45.0
    occupancy: int = 2
    hvac_on: bool = False


def step_temperature(state: RoomState, dt: float) -> float:
    q_people = state.occupancy * HEAT_PER_PERSON_W
    q_outdoor = WALL_K * (T_OUTDOOR - state.temperature)
    q_ac = -AC_POWER_W if state.hvac_on else 0.0
    t_next = state.temperature + (dt / ROOM_HEAT_CAPACITY) * (q_people + q_outdoor + q_ac)
    return clamp(t_next, TEMP_MIN, TEMP_MAX)


def step_humidity(state: RoomState, dt: float) -> float:
    rate = state.occupancy * HUMIDITY_PER_PERSON - (AC_DRY_RATE if state.hvac_on else 0.0)
    return clamp(state.humidity + rate * dt, HUM_MIN, HUM_MAX)


def step_occupancy(state: RoomState, rng: random.Random) -> int:
    delta = rng.choice([-1, 0, 0, 1])  # thien ve dung yen cho tu nhien
    return clamp(state.occupancy + delta, OCC_MIN, OCC_MAX)
