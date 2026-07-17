---
workflow: general-video
flow: automation
storyboard: no
aspect: "16:9"
language: en
duration_target: "~4.5–5 min"
---

# Smart Lab Digital Twin — Demo Video

## Goal
A narrated walkthrough video of the Smart Lab Digital Twin project, built from the
existing `report/demo_script.md` and the 8 dashboard/3D screenshots in `report/demo/`.
For a class/project submission and general demo use.

## Source material
- Narration: adapted (lightly condensed) from `report/demo_script.md`, English.
- Visuals: 8 PNG screenshots (1600×1000 / 2000×1250) staged in `assets/shots/`.
- Voice: local Kokoro TTS, voice `af_heart`. Per-scene wavs in `assets/audio/`.

## Shape
Modular composition, 16:9 (1920×1080), ~9 scenes:
1. Title + animated MQTT data-flow pipeline (intro narration).
2. Dashboard tour (demo_01) — sweeping callouts over each region.
3. The problem: room heats up (demo_02) — overheating alert.
4. PID at full power (demo_03) — AC on, 100%.
5. PID locked at setpoint (demo_04) — temperature holds 22°C.
6. Digital-twin feedback loop (demo_05) — setpoint round-trip over MQTT.
7. 3D room view (demo_06) — Three.js, WebSockets.
8. MQTT command interface & resilience (demo_07).
9. Recap / outro (demo_08).

Each screenshot scene = a framed "device-surface-showcase": hero screenshot with a
subtle ken-burns push, a scene title/lower-third, and spring-pop callout highlights
timed to the narration. Sequential scenes with short cross-dissolves; continuous dark
tech background; per-scene narration audio at the root.

## Design
Dark engineering aesthetic. See `frame.md`.
