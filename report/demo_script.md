# Smart Lab Digital Twin — Video Demo Script

**Target length:** ~6–7 minutes
**Format:** Screen recording with voice-over. Each scene lists what to show on screen, what to do, and the suggested narration.

---

## Pre-recording Checklist

1. Start the stack:
   ```bash
   docker compose up -d                                  # Mosquitto broker
   uv run simulator/publisher.py                         # Terminal 1
   uv run streamlit run dashboard/app.py                 # Terminal 2
   uv run python -m http.server 8000 --directory room3d  # Terminal 3
   ```
2. Open `http://localhost:8501` (dashboard) and `http://localhost:8000` (standalone 3D view) in separate browser tabs.
3. Reset to a clean baseline: HVAC **OFF**, occupancy low (~2 people), setpoint 24 °C, timescale ×1.
4. Keep one terminal visible for the MQTT command demo (Scene 7).
5. Close notifications / unrelated windows; set browser zoom so the full dashboard fits.

---

## Scene 1 — Introduction (0:00 – 0:40)

**On screen:** Title slide or README, then a quick glance at the architecture diagram (`docs/architecture.md`).

**Narration:**
> "Hi, this is a demo of the Smart Lab Digital Twin — a real-time digital twin of a laboratory room. A physics simulator models the room's temperature, humidity, and occupancy. It streams telemetry over MQTT to a Streamlit dashboard and an interactive Three.js 3D view. Crucially, this is a true digital twin, not just a digital shadow: commands flow back from the dashboard to the simulator, closing the loop. On top of that, a PID controller automatically regulates the air-conditioning power to hold any target temperature."

**Action:** Briefly scroll the 6-layer architecture diagram: Simulator → MQTT broker → Dashboard/3D view → User commands → back to Simulator.

---

## Scene 2 — Dashboard Tour (0:40 – 1:30)

**On screen:** The Streamlit dashboard at `http://localhost:8501`.

**Narration:**
> "This is the main dashboard. At the top we have live metrics — room temperature, humidity, and occupancy — updated every few seconds over MQTT. Here is the HVAC status panel, showing whether the AC is on and its current cooling power as a percentage. Below, a temperature trend chart with a predictive alert, and an inline 3D view of the room. On the left, the control panel: AC on/off, target setpoint, occupancy override, and simulation time-scale."

**Action:** Move the cursor slowly over each area as it's mentioned: metric cards → HVAC panel → chart → 3D view → control panel. Point out the `online` status indicator (Last Will & Testament).

---

## Scene 3 — The Problem: Room Heats Up (1:30 – 2:20)

**On screen:** Dashboard. Set timescale to **×10** so changes are visible quickly.

**Action & Narration:**
1. Set occupancy to **25 people**.
   > "Let's simulate a busy lab session — I'll override occupancy to 25 people. Each person adds heat load, roughly a hundred watts each, so the room now has around 2.5 kilowatts of internal heat."
2. Let it run 20–30 seconds; watch temperature climb on the chart.
   > "With the AC off, the temperature climbs steadily. Notice the predictive alert on the chart warning that the room will overheat if nothing changes."
3. Switch to the 3D view briefly.
   > "In the 3D view, you can see people walking in through the automatic sliding doors as occupancy rises, and the floor turning red as the room gets hot."

---

## Scene 4 — Closed-Loop Control: PID in Action (2:20 – 3:40)

**On screen:** Dashboard, HVAC panel and temperature chart in view.

**Action & Narration:**
1. Turn **AC ON**, setpoint **22 °C**.
   > "Now I turn the AC on with a 22-degree setpoint. The PID controller takes over: it measures the error between room temperature and setpoint, and modulates the AC power continuously from 0 to 100 percent of its 3.5-kilowatt capacity."
2. Watch `ac_power_pct` jump to ~100 %, then temperature fall.
   > "With a large error, the proportional term drives the AC to full power. As the temperature approaches the setpoint, power backs off smoothly instead of crudely switching on and off."
3. Wait until temperature locks onto 22 °C with the AC at a partial, steady power.
   > "And here's the key result: the temperature locks onto exactly 22 degrees, even with 25 people inside. The integral term eliminates the steady-state offset that a simple proportional controller would leave, and the derivative term damps the overshoot. Anti-windup keeps the controller responsive even after long periods at full power."

---

## Scene 5 — Digital Twin Feedback Loop (3:40 – 4:30)

**On screen:** Dashboard control panel and HVAC status side by side.

**Action & Narration:**
1. Change the setpoint from 22 → **25 °C**.
   > "Watch what happens when I change the setpoint. The dashboard doesn't just assume the new value — it publishes a command over MQTT, the simulator applies it, and the *confirmed* state comes back and updates the display. That round trip is what makes this a digital twin rather than a one-way shadow."
2. Show AC power dropping (room is already cooler than the new setpoint), then stabilizing at 25 °C.
   > "The controller immediately reduces power since the room is now below target, and re-converges on the new setpoint."

---

## Scene 6 — 3D Room View (4:30 – 5:20)

**On screen:** Standalone 3D view at `http://localhost:8000` (or the inline view, full screen).

**Action & Narration:**
1. Orbit the camera around the lab and corridor.
   > "The 3D view is built with Three.js and subscribes to the same MQTT topics directly from the browser over WebSockets — no extra backend needed."
2. Drop occupancy to **5**; watch people walk out through the sliding doors.
   > "When I lower occupancy on the dashboard, characters walk out through the automatic glass doors in real time."
3. Point at floor color.
   > "The floor color encodes temperature — blue when the room is at setpoint, shifting toward red as it heats up."

---

## Scene 7 — MQTT Command Interface & Resilience (5:20 – 6:10)

**On screen:** Terminal next to the dashboard.

**Action & Narration:**
1. Publish a command from the terminal:
   ```bash
   docker exec mosquitto mosquitto_pub -t twin/room1/cmd/occupancy -m '{"value": 30}'
   ```
   > "Everything is driven by open MQTT topics, so any client can participate. Here I set occupancy to 30 straight from the command line — and the dashboard and 3D view both react instantly."
2. (Optional) Stop the simulator with Ctrl-C; show the dashboard flipping to `offline`.
   > "If the simulator dies, the broker's Last Will and Testament immediately marks the twin offline on the dashboard. Restarting it, retained messages restore the latest state instantly."
3. Restart the simulator.

---

## Scene 8 — Wrap-up (6:10 – 6:40)

**On screen:** Architecture diagram again, or the dashboard in steady state at setpoint.

**Narration:**
> "To recap: a physics-based room simulator, event-driven MQTT communication with retained state and failure detection, a live dashboard and 3D visualization, and a closed feedback loop with an auto-regulating PID controller — together forming a complete, real-time digital twin of a smart laboratory. Thanks for watching."

---

## Backup / B-roll Ideas

- Terminal running `uv run pytest -v` with all unit tests passing.
- Close-up of the PID gains in `simulator/pid_controller.py` while narrating the Kp/Ki/Kd roles.
- Side-by-side of dashboard chart and 3D floor color during a cool-down.

## Recording Tips

- Record at ×10 timescale for all thermal transitions; cut dead time in editing.
- Capture Scenes 3–5 in one continuous take so the chart history tells the story.
- Keep the mouse still while narrating; move it only to point at what's being described.
