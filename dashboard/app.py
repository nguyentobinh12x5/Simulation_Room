"""Dashboard Streamlit: hien thi real-time + dieu khien AC (Task 5)."""
import json
import threading
from collections import deque
from datetime import datetime

import numpy as np
import paho.mqtt.client as mqtt
import plotly.graph_objects as go
import streamlit as st

BROKER_HOST = "localhost"
BROKER_PORT = 1883
BASE = "twin/room1"
SENSORS = ("temperature", "humidity", "occupancy")
ALERT_ON, ALERT_OFF = 30.0, 29.5  # hysteresis chong nhap nhay


@st.cache_resource
def get_mqtt():
    """1 client + 1 buffer duy nhat cho ca app — song sot qua moi lan rerun."""
    store = {
        "temperature": deque(maxlen=100),  # ~5 phut @ 3s
        "humidity": deque(maxlen=60),
        "occupancy": deque(maxlen=150),
        "hvac_on": None,
        "status": "unknown",
        "lock": threading.Lock(),
    }

    def on_connect(client, userdata, flags, reason_code, properties):
        client.subscribe([(f"{BASE}/{s}", 0) for s in SENSORS]
                         + [(f"{BASE}/hvac/state", 0), (f"{BASE}/status", 0)])

    def on_message(client, userdata, msg):
        with store["lock"]:
            if msg.topic == f"{BASE}/status":
                store["status"] = msg.payload.decode()
                return
            try:
                data = json.loads(msg.payload)
            except json.JSONDecodeError:
                return
            if msg.topic == f"{BASE}/hvac/state":
                store["hvac_on"] = data.get("hvac_on")
            else:
                sensor = msg.topic.rsplit("/", 1)[-1]
                ts = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                store[sensor].append((ts, data["value"]))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT)
    client.loop_start()
    return client, store


def latest(store, sensor):
    with store["lock"]:
        return store[sensor][-1][1] if store[sensor] else None


st.set_page_config(page_title="Smart Lab Digital Twin", layout="wide")
st.title("Smart Lab Digital Twin — Room 1")
client, store = get_mqtt()
if "alert_on" not in st.session_state:
    st.session_state.alert_on = False

with st.sidebar:
    st.header("Điều khiển")
    col_on, col_off = st.columns(2)
    if col_on.button("❄️ AC ON", use_container_width=True):
        client.publish(f"{BASE}/cmd/hvac", json.dumps({"command": "on"}))
    if col_off.button("AC OFF", use_container_width=True):
        client.publish(f"{BASE}/cmd/hvac", json.dumps({"command": "off"}))
    st.caption("Trạng thái AC lấy từ twin/room1/hvac/state — "
               "là trạng thái simulator xác nhận, không phải trạng thái nút.")


@st.fragment(run_every=1.0)
def live_view():
    temp = latest(store, "temperature")
    hum = latest(store, "humidity")
    occ = latest(store, "occupancy")

    if store["status"] == "offline":
        st.warning("Simulator offline — dữ liệu bên dưới là giá trị cuối cùng.")

    # Alert banner voi hysteresis
    if temp is not None:
        if temp > ALERT_ON:
            st.session_state.alert_on = True
        elif temp < ALERT_OFF:
            st.session_state.alert_on = False
    if st.session_state.alert_on:
        st.error(f"🔥 QUÁ NHIỆT: {temp:.1f}°C (ngưỡng {ALERT_ON}°C)")

    c1, c2, c3 = st.columns(3)
    c1.metric("🌡 Temperature", f"{temp:.1f} °C" if temp is not None else "—")
    c2.metric("💧 Humidity", f"{hum:.1f} %" if hum is not None else "—")
    c3.metric("👥 Occupancy", f"{occ} người" if occ is not None else "—")

    hvac = store["hvac_on"]
    if hvac is None:
        st.caption("AC: chưa rõ (chưa nhận state)")
    else:
        st.markdown(f"**AC:** {'🟢 ON' if hvac else '⚪ OFF'}")

    with store["lock"]:
        points = list(store["temperature"])
    if points:
        xs, ys = zip(*points)
        fig = go.Figure(go.Scatter(x=list(xs), y=list(ys), mode="lines"))
        fig.add_hline(y=ALERT_ON, line_dash="dash", line_color="red",
                      annotation_text="ngưỡng alert 30°C")
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10),
                          yaxis_title="°C", title="Nhiệt độ (~5 phút gần nhất)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Đang chờ dữ liệu từ simulator…")

    # Du bao: fit bac 1 qua 60s gan nhat, uoc luong thoi gian cham 30°C
    if len(points) >= 5:
        now = xs[-1]
        recent = [(x, y) for x, y in points if (now - x).total_seconds() <= 60]
        if len(recent) >= 5:
            t0 = recent[0][0]
            sec = np.array([(x - t0).total_seconds() for x, _ in recent])
            vals = np.array([y for _, y in recent])
            slope, intercept = np.polyfit(sec, vals, 1)
            if slope > 0.001 and vals[-1] < ALERT_ON:
                eta = (ALERT_ON - vals[-1]) / slope
                if eta < 300:
                    st.warning(f"📈 Dự báo chạm {ALERT_ON}°C sau ~{eta:.0f}s "
                               f"(tốc độ +{slope*60:.2f}°C/phút)")


live_view()
