# Build Spec — Smart Lab Digital Twin

Đây là spec kỹ thuật để đưa cho Claude Code làm theo. Build theo đúng thứ tự các
Module bên dưới — mỗi Module có "Definition of done" riêng, không chuyển sang
Module tiếp theo khi module hiện tại chưa qua được checklist đó.

## Bối cảnh đề bài

Xây "Connected Digital Twin" của 1 phòng lab ảo, dùng dữ liệu sensor giả lập
để tạo "Digital Thread" sống. Đề bài yêu cầu mức **digital shadow** (dữ liệu
chảy 1 chiều sensor → dashboard). Nhóm nâng lên **digital twin thật** bằng
cách thêm kênh điều khiển ngược: dashboard → simulator (đóng vòng lặp).

## Tech stack đã chốt

- **Broker:** Eclipse Mosquitto (Docker), cả MQTT thường (1883) và WebSocket (9001)
- **Simulator:** Python + `paho-mqtt`
- **Dashboard:** Streamlit + `paho-mqtt` + `plotly`/`st.line_chart`
- **3D (optional, Module 5):** Three.js (CDN, không build step) + `mqtt.js` qua WebSocket
- **Diagram/report:** làm riêng, không phải code

## Cấu trúc repo đề xuất

```
digital-twin-lab/
├── docker-compose.yml          # Mosquitto broker
├── mosquitto/
│   └── config/mosquitto.conf   # bật cả port 1883 + 9001 websocket
├── simulator/
│   ├── physics.py              # công thức tính nhiệt/ẩm/occupancy
│   ├── publisher.py            # publish loop, đọc physics.py
│   └── requirements.txt
├── dashboard/
│   ├── app.py                  # Streamlit app chính
│   └── requirements.txt
├── room3d/
│   └── room3d.html             # (Module 5, optional) Three.js scene
└── README.md
```

---

## Module 1 — Broker

`docker-compose.yml` chạy Mosquitto, expose 2 port:

```
1883  -> MQTT chuẩn (dùng cho simulator, Python)
9001  -> MQTT over WebSocket (dùng cho browser/3D nếu làm Module 5)
```

`mosquitto.conf` tối thiểu:
```
listener 1883
listener 9001
protocol websockets
allow_anonymous true
```

**Definition of done:** `mosquitto_pub`/`mosquitto_sub` test thủ công gửi/nhận
được message trên topic bất kỳ.

---

## Module 2 — Simulator

### Topic structure

```
twin/room1/temperature
twin/room1/humidity
twin/room1/occupancy
twin/room1/cmd/hvac        <- subscribe (lệnh điều khiển, chiều ngược)
```

### Payload format (JSON)

```json
{"sensor": "temperature", "value": 24.7, "unit": "C", "timestamp": "2026-07-16T20:14:03Z"}
{"sensor": "humidity", "value": 45.2, "unit": "%", "timestamp": "..."}
{"sensor": "occupancy", "value": 3, "unit": "people", "timestamp": "..."}
```

Lệnh điều khiển gửi vào `twin/room1/cmd/hvac`:
```json
{"command": "on"}
{"command": "off"}
```

### Update frequency

| Sensor | Chu kỳ | Range bình thường | Ngưỡng alert |
|---|---|---|---|
| temperature | 3s | 20–28°C | > 30°C |
| humidity | 5s | 30–60% | < 20% hoặc > 70% |
| occupancy | 2s | 0–6 người | > 8 |

### Physics model (không dùng random thuần)

State giữ trong bộ nhớ: `temperature`, `humidity`, `occupancy`, `hvac_on`.

```python
# Mỗi bước thời gian dt (giây):
Q_people  = occupancy * 100        # W, mỗi người tỏa ~100W
Q_outdoor = k * (T_outdoor - T)     # truyền nhiệt qua tường, k ~ 0.05
Q_ac      = -800 if hvac_on else 0  # AC rút nhiệt khi bật

T_next = T + (dt / C) * (Q_people + Q_outdoor + Q_ac)
# C (nhiệt dung phòng) chọn giá trị sao cho nhiệt tăng ~0.3-0.5°C mỗi 15s
# khi occupancy=8, và giảm về bình thường trong ~60-90s sau khi bật AC

humidity_next = humidity + occupancy * 0.3 - (5 if hvac_on else 0)
humidity_next = clamp(humidity_next, 15, 80)

# occupancy: random walk bước nguyên (+1/0/-1), không đổi bởi AC
```

Clamp mọi giá trị trong range hợp lý. Nhiễu nhỏ (`+/- 0.1`) có thể cộng thêm
để trông tự nhiên, nhưng xu hướng chính phải theo công thức trên.

### Closed-loop control

Simulator subscribe `twin/room1/cmd/hvac`. Khi nhận `{"command": "on"}` →
set `hvac_on = True` (ảnh hưởng công thức trên ngay từ bước tiếp theo). Nhận
`"off"` → `hvac_on = False`.

**Definition of done:**
- Publish đều 3 topic đúng chu kỳ, đúng format JSON
- Chạy kịch bản thủ công: set occupancy=8 giả lập → thấy temperature tăng dần theo log
- Publish `{"command":"on"}` vào topic cmd → thấy temperature bắt đầu giảm trong log

---

## Module 3 — Dashboard (Streamlit)

### UI cần có (bắt buộc — Tier 1)

- 3 metric card: temperature / humidity / occupancy, cập nhật real-time
- Line chart nhiệt độ theo thời gian (giữ ~2-5 phút gần nhất)
- Alert banner đỏ khi `temperature > 30°C`, tự ẩn khi hạ nhiệt

### UI nâng cấp (Tier 2)

- Nút "Turn AC on/off" — khi bấm, publish lệnh lên `twin/room1/cmd/hvac`
- Hiển thị trạng thái AC hiện tại (on/off)
- (tuỳ chọn) Predictive alert: fit đường thẳng qua 60s gần nhất
  (`numpy.polyfit` bậc 1), ước tính bao lâu nữa chạm 30°C

### Lưu ý kỹ thuật quan trọng — MQTT client trong Streamlit

Streamlit rerun toàn bộ script liên tục — **không** tạo MQTT client mới mỗi
lần rerun. Dùng `st.session_state` để giữ 1 client instance duy nhất, hoặc
chạy MQTT client trong 1 background thread ghi vào 1 buffer, Streamlit chỉ
đọc buffer đó mỗi lần rerun.

**Definition of done:**
- Chạy simulator + dashboard cùng lúc, thấy số liệu update live không lag,
  không bị duplicate connection
- Alert xuất hiện đúng lúc temp > 30°C trong lần chạy thật

---

## Module 4 — Architecture Diagram & Technical Summary

(Không phải code — làm sau khi Module 2+3 chạy ổn, dùng nội dung ở đây làm
tư liệu.)

- Diagram: 6 layer, có mũi tên ngược từ Dashboard → Connectivity → Simulator
  thể hiện lệnh điều khiển
- Technical Summary: giải thích lý do chọn MQTT (pub/sub, nhẹ, decoupled so
  với CSV tĩnh/HTTP polling), và lý do nâng từ digital shadow lên digital
  twin bằng closed-loop

---

## Module 5 — 3D Visualization (stretch, chỉ làm nếu Module 2+3 đã ổn)

- 1 file `room3d.html` độc lập, không phụ thuộc Streamlit
- Three.js load từ CDN, subscribe MQTT qua `mqtt.js` tại `ws://localhost:9001`
- Room: 1 box đơn giản (sàn + 4 tường)
- Temperature → lerp màu sàn xanh (20°C) → đỏ (32°C)
- Occupancy → spawn/xóa `THREE.CapsuleGeometry` theo số người
- HVAC on → xoay 1 mesh quạt (`rotation.y += delta`)
- Nhúng vào Streamlit: `st.components.v1.html(open("room3d.html").read(), height=500)`
  — **giữ chuỗi HTML tĩnh, không f-string chèn giá trị Python vào**, nếu
  không iframe sẽ bị reload mỗi lần Streamlit rerun

**Time-box: tối đa 3-4 tiếng.** Không chạy mượt trong khung đó → cắt, gỡ
khỏi dashboard, không nhắc trong report.

---

## Thứ tự build (map với lịch làm việc)

1. Module 1 (Broker) — Thứ 5
2. Module 2 phần publish cơ bản (random walk trước, chưa cần physics) — Thứ 5
3. Module 3 Tier 1 (dashboard live + alert) — Thứ 6 — **checkpoint an toàn**
4. Module 2 nâng cấp physics thật + closed-loop, Module 3 Tier 2 (nút AC) — Thứ 7 sáng
5. Module 4 (diagram + summary) — Thứ 7 chiều
6. Module 5 (3D, optional) — Thứ 7 chiều, time-boxed
7. Polish, demo, nộp — Chủ nhật
