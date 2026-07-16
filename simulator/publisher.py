"""Simulator: publish sensor data va nhan lenh dieu khien nguoc (closed-loop)."""
import json
import random
import time
from dataclasses import replace
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from physics import (OCC_MAX, OCC_MIN, RoomState, clamp, step_humidity,
                     step_occupancy, step_temperature)

BROKER_HOST = "localhost"
BROKER_PORT = 1883
BASE = "twin/room1"
CMD_HVAC = f"{BASE}/cmd/hvac"
CMD_OCCUPANCY = f"{BASE}/cmd/occupancy"
STATUS_TOPIC = f"{BASE}/status"
HVAC_STATE_TOPIC = f"{BASE}/hvac/state"

INTERVALS = {"temperature": 3, "humidity": 5, "occupancy": 2}
NOISE = 0.1


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_payload(sensor: str, value, unit: str, timestamp: str | None = None) -> str:
    return json.dumps({"sensor": sensor, "value": value, "unit": unit,
                       "timestamp": timestamp or utc_now_iso()})


def handle_command(state: RoomState, topic: str, payload: bytes) -> RoomState:
    """Ap lenh dieu khien vao state; lenh hong thi bo qua, state giu nguyen."""
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return state
    if not isinstance(data, dict):
        return state
    if topic == CMD_HVAC:
        cmd = data.get("command")
        if cmd in ("on", "off"):
            return replace(state, hvac_on=(cmd == "on"))
    elif topic == CMD_OCCUPANCY:
        v = data.get("value")
        if isinstance(v, int) and not isinstance(v, bool):
            return replace(state, occupancy=clamp(v, OCC_MIN, OCC_MAX))
    return state


class Simulator:
    def __init__(self):
        self.state = RoomState()
        self.rng = random.Random()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.will_set(STATUS_TOPIC, "offline", retain=True)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, reason_code, properties):
        client.subscribe([(CMD_HVAC, 0), (CMD_OCCUPANCY, 0)])
        client.publish(STATUS_TOPIC, "online", retain=True)
        self.publish_hvac_state()
        print("connected, subscribed to cmd topics")

    def on_message(self, client, userdata, msg):
        before = self.state.hvac_on
        self.state = handle_command(self.state, msg.topic, msg.payload)
        print(f"cmd {msg.topic}: {msg.payload!r} -> hvac_on={self.state.hvac_on}, "
              f"occupancy={self.state.occupancy}")
        if self.state.hvac_on != before:
            self.publish_hvac_state()

    def publish_hvac_state(self):
        self.client.publish(HVAC_STATE_TOPIC,
                            json.dumps({"hvac_on": self.state.hvac_on,
                                        "timestamp": utc_now_iso()}),
                            retain=True)

    def publish_sensor(self, sensor: str):
        if sensor == "temperature":
            value, unit = round(self.state.temperature + self.rng.uniform(-NOISE, NOISE), 2), "C"
        elif sensor == "humidity":
            value, unit = round(self.state.humidity + self.rng.uniform(-NOISE, NOISE), 2), "%"
        else:
            value, unit = self.state.occupancy, "people"
        self.client.publish(f"{BASE}/{sensor}", make_payload(sensor, value, unit), retain=True)
        print(f"{sensor}={value}{unit} hvac={'on' if self.state.hvac_on else 'off'}")

    def run(self):
        self.client.connect(BROKER_HOST, BROKER_PORT)
        self.client.loop_start()  # cmd xu ly o thread rieng cua paho
        tick = 0
        try:
            while True:
                # physics tien 1 giay moi tick, khong phu thuoc chu ky publish
                self.state = replace(
                    self.state,
                    temperature=step_temperature(self.state, dt=1.0),
                    humidity=step_humidity(self.state, dt=1.0),
                )
                if tick % INTERVALS["occupancy"] == 0:
                    self.state = replace(self.state,
                                         occupancy=step_occupancy(self.state, self.rng))
                for sensor, interval in INTERVALS.items():
                    if tick % interval == 0:
                        self.publish_sensor(sensor)
                tick += 1
                time.sleep(1)
        except KeyboardInterrupt:
            self.client.publish(STATUS_TOPIC, "offline", retain=True)
            self.client.loop_stop()


if __name__ == "__main__":
    Simulator().run()
