# Smart Lab Digital Twin

A real-time laboratory room Digital Twin: Physics Simulator → MQTT → Dashboard & 3D WebGL View, featuring closed-loop HVAC automation controlled by an auto-tuning PID algorithm.

Detailed technical architecture: [docs/architecture.md](docs/architecture.md).

---

## Key Features

- **Dynamic HVAC**: Variable AC power output ranging from 0% to 100% (max 3500W).
- **AI-Powered Controller (PID)**: Proportional-Integral-Derivative feedback loop that automatically regulates AC cooling power to achieve and lock onto your target temperature (setpoint), eliminating steady-state errors under high loads.
- **Large Capacity Support**: Simulated workspace supporting up to 30 people with dynamic thermal loads.
- **Time Acceleration**: Fast-forward simulation cycles (x1, x2, x5, x10) to observe thermal transitions instantly.
- **Interactive 3D Room**: Built using Three.js, rendering a laboratory alongside an outer corridor. It animates people walking through automatic sliding glass doors in real-time as occupancy fluctuates. Floor colors shift dynamically from blue (setpoint reached) to red (hot) based on room temperature.
- **Centralized Dashboard**: Compact layout presenting parameters, HVAC status, temperature trend charts with predictive alerts, and inline 3D visualization.

---

## Running the Application

1. **Start the MQTT Broker**
   ```bash
   docker compose up -d                  # Mosquito broker runs on :1883 and WS :9001
   ```

2. **Setup Dependencies**
   * **Using `uv` (Recommended - fast & auto-managed)**:
     No manual virtual environment activation required! Simply run:
     ```bash
     uv sync
     ```
   * **Traditional way**:
     ```bash
     python3 -m venv .venv && source .venv/bin/activate
     pip install -r simulator/requirements.txt -r dashboard/requirements.txt
     ```

3. **Launch Components**
   * **Using `uv`**:
     * **Terminal 1: Simulator Publisher**
       ```bash
       uv run simulator/publisher.py
       ```
     * **Terminal 2: Dashboard UI (Streamlit)**
       ```bash
       uv run streamlit run dashboard/app.py
       ```
     * **Terminal 3: 3D Room View Web Server**
       ```bash
       uv run python -m http.server 8000 --directory room3d
       ```
   * **Traditional way**:
     * **Terminal 1: Simulator Publisher**
       ```bash
       python simulator/publisher.py
       ```
     * **Terminal 2: Dashboard UI (Streamlit)**
       ```bash
       streamlit run dashboard/app.py
       ```
     * **Terminal 3: 3D Room View Web Server**
       ```bash
       python3 -m http.server 8000 --directory room3d
       ```

Open your browser at `http://localhost:8501` to access the main interface.

---

## Command Interface (MQTT)

You can send direct commands to the simulator using MQTT publish:

```bash
# Override room occupancy to 25 people
docker exec mosquitto mosquitto_pub -t twin/room1/cmd/occupancy -m '{"value": 25}'

# Set the target temperature to 22.5°C
docker exec mosquitto mosquitto_pub -t twin/room1/cmd/setpoint -m '{"value": 22.5}'

# Speed up the simulation by 10x
docker exec mosquitto mosquitto_pub -t twin/room1/cmd/timescale -m '{"value": 10}'

# Enable AC (PID automatically turns on to drive temperature to setpoint)
docker exec mosquitto mosquitto_pub -t twin/room1/cmd/hvac -m '{"command": "on"}'

# Disable AC
docker exec mosquitto mosquitto_pub -t twin/room1/cmd/hvac -m '{"command": "off"}'
```

---

## MQTT Topic Table

| Topic | Direction | Payload | Retained |
|---|---|---|---|
| `twin/room1/temperature` | Sim → Dash | `{"sensor", "value", "unit", "timestamp"}` (every 3s) | Yes |
| `twin/room1/humidity` | Sim → Dash | `{"sensor", "value", "unit", "timestamp"}` (every 5s) | Yes |
| `twin/room1/occupancy` | Sim → Dash | `{"sensor", "value", "unit", "timestamp"}` (every 2s) | Yes |
| `twin/room1/cmd/hvac` | Dash → Sim | `{"command": "on"\|"off"}` | No |
| `twin/room1/cmd/occupancy` | Dash → Sim | `{"value": <int 0-30>}` | No |
| `twin/room1/cmd/setpoint` | Dash → Sim | `{"value": <float 18.0-30.0>}` | No |
| `twin/room1/cmd/timescale` | Dash → Sim | `{"value": <int 1\|2\|5\|10>}` | No |
| `twin/room1/hvac/state` | Sim → Dash | `{"hvac_on", "ac_power_pct", "setpoint", "timestamp"}` | Yes |
| `twin/room1/ac/detail` | Sim → Dash | `{"ac_power_pct", "ac_temp_output", "setpoint", "mode", "timestamp"}` | Yes |
| `twin/room1/status` | Sim → Dash | `online` / `offline` (Last Will & Testament) | Yes |

---

## Running Unit Tests

* **Using `uv`**:
  ```bash
  uv run pytest -v
  ```
* **Traditional way**:
  Ensure the python virtual environment is active, then run:
  ```bash
  cd simulator && python -m pytest tests/ -v
  ```
All 32 tests will run to verify physical step calculations, PID controller limits, and MQTT command handling.
