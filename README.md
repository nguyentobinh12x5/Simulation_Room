# Smart Lab Digital Twin

Digital twin của 1 phòng lab ảo: simulator vật lý → MQTT → dashboard
real-time, kèm điều khiển ngược HVAC (closed-loop). Kiến trúc chi tiết:
[docs/architecture.md](docs/architecture.md).

## Chạy

```bash
docker compose up -d                       # broker :1883 + :9001
python3 -m venv .venv && source .venv/bin/activate
pip install -r simulator/requirements.txt -r dashboard/requirements.txt

python simulator/publisher.py              # terminal 1
streamlit run dashboard/app.py             # terminal 2
```

## Demo script

```bash
# Ép phòng đông người -> nhiệt tăng, predictive alert, rồi alert đỏ
docker exec mosquitto mosquitto_pub -t twin/room1/cmd/occupancy -m '{"value": 10}'
# Bấm "AC ON" trên dashboard (hoặc:)
docker exec mosquitto mosquitto_pub -t twin/room1/cmd/hvac -m '{"command": "on"}'
```

## Topics

| Topic | Chiều | Nội dung |
|---|---|---|
| `twin/room1/temperature` | sim → dash | `{"sensor","value","unit","timestamp"}`, 3s, retained |
| `twin/room1/humidity` | sim → dash | như trên, 5s |
| `twin/room1/occupancy` | sim → dash | như trên, 2s |
| `twin/room1/cmd/hvac` | dash → sim | `{"command": "on"\|"off"}` |
| `twin/room1/cmd/occupancy` | demo → sim | `{"value": <int 0-10>}` |
| `twin/room1/hvac/state` | sim → dash | trạng thái AC xác nhận, retained |
| `twin/room1/status` | sim → dash | `online`/`offline` (LWT), retained |

## Test

```bash
cd simulator && python -m pytest tests/ -v
```
