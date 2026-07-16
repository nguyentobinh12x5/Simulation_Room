# Kiến trúc — Smart Lab Digital Twin

## Diagram 6 layer (mũi tên ngược = closed-loop)

```mermaid
flowchart TB
    subgraph L1["1. Physical/Simulated Layer"]
        SIM["Simulator (physics.py + publisher.py)\nstate: temp, humidity, occupancy, hvac"]
    end
    subgraph L2["2. Data Acquisition"]
        PUB["paho-mqtt publish\n3 topic sensor, chu kỳ 2-5s, JSON"]
    end
    subgraph L3["3. Connectivity"]
        BROKER["Mosquitto broker\n1883 MQTT / 9001 WebSocket"]
    end
    subgraph L4["4. Data Processing"]
        BUF["Background MQTT thread\ndeque buffer + lock"]
    end
    subgraph L5["5. Application"]
        DASH["Streamlit dashboard\nmetrics, chart, alert, predictive"]
    end
    subgraph L6["6. Interaction"]
        USER["Người dùng\nnút AC ON/OFF, xem 3D"]
    end
    SIM --> PUB --> BROKER --> BUF --> DASH --> USER
    USER -. "cmd" .-> DASH
    DASH -. "twin/room1/cmd/hvac" .-> BROKER
    BROKER -. "subscribe cmd" .-> SIM
```

## Technical Summary

**Vì sao MQTT thay vì CSV tĩnh / HTTP polling?** Pub/sub tách rời producer
và consumer: simulator không cần biết ai đang nghe, dashboard và trang 3D
cùng subscribe một nguồn dữ liệu mà không thêm tải cho simulator. MQTT nhẹ
(header vài byte), có sẵn retained message (client mới vào nhận ngay giá
trị cuối) và Last-Will (phát hiện simulator rớt mạng) — những thứ HTTP
polling phải tự xây. CSV tĩnh thì không có chiều real-time lẫn chiều điều
khiển ngược.

**Vì sao đây là digital twin, không chỉ digital shadow?** Shadow chỉ có
dòng dữ liệu 1 chiều sensor → dashboard. Hệ này đóng vòng lặp: dashboard
publish lệnh vào `twin/room1/cmd/hvac`, simulator đổi physics ngay bước
tiếp theo, và xác nhận qua `twin/room1/hvac/state` (retained) — dashboard
hiển thị trạng thái *được xác nhận*, không phải trạng thái đoán. Digital
model → shadow → twin khác nhau đúng ở mức độ tự động của 2 chiều dữ liệu;
chiều ngược tự động này là tiêu chí phân loại twin.
