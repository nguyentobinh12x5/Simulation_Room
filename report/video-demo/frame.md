# Design Spec — Smart Lab Digital Twin demo

## Concept angle
"Mission-control for a room." A calm, dark engineering console that frames real
product screenshots like telemetry on a monitoring wall — precise, technical, trustworthy.

## Palette (dark)
- Background base: `#0a0f1c` (deep navy-black), with a subtle radial glow `#101a2e`.
- Panel / card surface: `#111a2b` at 70–85% with a 1px hairline border `#1f3350`.
- Primary accent (cyan/teal — MQTT, active): `#38e1c8`.
- Secondary accent (electric blue — data/cool): `#4c8dff`.
- Heat accent (warm/alert): `#ff6b4a` → `#ffb020` gradient.
- Cool/setpoint: `#3fa9ff`.
- Text primary: `#eaf2ff`; muted: `#8ea3c4`.

## Typography (system stack — reliable in local render)
- Display / headings: `"SF Pro Display", "Helvetica Neue", Inter, system-ui, sans-serif`, weight 700–800, tight tracking.
- Body / labels: same sans, weight 400–600.
- Mono (topic names, values, code): `"SF Mono", "JetBrains Mono", Menlo, monospace`.

## Layout system (1920×1080)
- Global 96px side safe-margin for text; screenshots sit in a rounded "device" frame
  (`border-radius: 20px`, hairline border, soft drop shadow, slight inner vignette).
- Persistent top-left kicker: `SMART LAB · DIGITAL TWIN` in mono, cyan.
- Per-scene lower-third title bar: scene number + title, left-aligned, with an accent tick.
- Callouts: rounded highlight rings/boxes (accent stroke, faint glow) with a short label
  pill and a connector — spring-pop in, hold, fade.

## Motion language
- Screenshots: slow ken-burns (scale 1.0→1.06 or a gentle pan), eased `power1.inOut`.
- Callouts: `back.out(1.7)` spring-pop scale-in, staggered to the narration.
- Scene transitions: 0.5s cross-dissolve (opacity + 8px slide), on overlapping tracks.
- Intro pipeline: nodes spring in left→right, animated dashed "packet" flow along links,
  a reverse "command" pulse to show the closed loop.
- Numbers/labels: brief count or fade; keep low-motion where the screenshot is the payload.

## Audio identity
- Narration (Kokoro `af_heart`) is the spine; each scene's VO sets its length.
- No music bed by default (technical clarity); optional soft ambient pad could be added later.
