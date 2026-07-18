# Smart Lab Digital Twin — Kịch bản Video Demo

**Thời lượng mục tiêu:** ~6–7 phút
**Định dạng:** Quay màn hình kèm thuyết minh (voice-over). Mỗi cảnh liệt kê nội dung hiển thị trên màn hình, thao tác cần làm, và lời thuyết minh gợi ý.

---

## Danh sách kiểm tra trước khi quay

1. Khởi động toàn bộ hệ thống:
   ```bash
   docker compose up -d                                  # Broker Mosquitto
   uv run simulator/publisher.py                         # Terminal 1
   uv run streamlit run dashboard/app.py                 # Terminal 2
   uv run python -m http.server 8000 --directory room3d  # Terminal 3
   ```
2. Mở `http://localhost:8501` (dashboard) và `http://localhost:8000` (chế độ xem 3D độc lập) trên hai tab trình duyệt riêng.
3. Đưa về trạng thái ban đầu sạch: HVAC **TẮT (OFF)**, số người thấp (~2 người), setpoint 24 °C, tốc độ mô phỏng ×1.
4. Giữ một cửa sổ terminal hiển thị để demo lệnh MQTT (Cảnh 7).
5. Tắt thông báo / các cửa sổ không liên quan; chỉnh mức zoom trình duyệt để hiển thị vừa toàn bộ dashboard.

---

## Cảnh 1 — Giới thiệu (0:00 – 0:40)

**Trên màn hình:** Slide tiêu đề hoặc README, sau đó lướt nhanh qua sơ đồ kiến trúc (`docs/architecture.md`).

**Thuyết minh:**
> "Xin chào, đây là bản demo của Smart Lab Digital Twin — một bản sao số (digital twin) thời gian thực của một phòng thí nghiệm. Một bộ mô phỏng vật lý sẽ mô hình hóa nhiệt độ, độ ẩm và số người trong phòng. Dữ liệu telemetry được truyền qua MQTT tới một dashboard Streamlit và một chế độ xem 3D tương tác dựng bằng Three.js. Quan trọng hơn, đây là một digital twin thực sự chứ không chỉ là 'bóng số' (digital shadow): các lệnh điều khiển được gửi ngược từ dashboard về bộ mô phỏng, khép kín vòng lặp. Bên cạnh đó, một bộ điều khiển PID tự động điều chỉnh công suất điều hòa để giữ nhiệt độ ở bất kỳ mức mục tiêu nào."

**Thao tác:** Lướt nhanh qua sơ đồ kiến trúc 6 lớp: Bộ mô phỏng → Broker MQTT → Dashboard/Chế độ xem 3D → Lệnh người dùng → quay lại Bộ mô phỏng.

---

## Cảnh 2 — Tham quan Dashboard (0:40 – 1:30)

**Trên màn hình:** Dashboard Streamlit tại `http://localhost:8501`.

**Thuyết minh:**
> "Đây là dashboard chính. Phía trên là các chỉ số trực tiếp — nhiệt độ phòng, độ ẩm và số người — được cập nhật vài giây một lần qua MQTT. Đây là bảng trạng thái HVAC, cho biết điều hòa đang bật hay tắt và công suất làm mát hiện tại tính theo phần trăm. Bên dưới là biểu đồ xu hướng nhiệt độ kèm cảnh báo dự đoán, và chế độ xem 3D nhúng ngay trong trang. Bên trái là bảng điều khiển: bật/tắt điều hòa, đặt nhiệt độ mục tiêu, ghi đè số người, và tỉ lệ tốc độ mô phỏng."

**Thao tác:** Di chuột chậm qua từng khu vực khi được nhắc đến: các thẻ chỉ số → bảng HVAC → biểu đồ → chế độ xem 3D → bảng điều khiển. Chỉ vào chỉ báo trạng thái `online` (Last Will & Testament).

---

## Cảnh 3 — Vấn đề: Phòng nóng lên (1:30 – 2:20)

**Trên màn hình:** Dashboard. Đặt tốc độ mô phỏng thành **×10** để thấy thay đổi diễn ra nhanh.

**Thao tác & Thuyết minh:**
1. Đặt số người thành **25**.
   > "Hãy mô phỏng một buổi làm việc đông đúc — tôi ghi đè số người lên 25. Mỗi người tỏa thêm nhiệt, khoảng một trăm watt mỗi người, nên bây giờ phòng có khoảng 2,5 kilowatt nhiệt sinh ra bên trong."
2. Để chạy 20–30 giây; quan sát nhiệt độ leo lên trên biểu đồ.
   > "Khi điều hòa tắt, nhiệt độ tăng đều. Chú ý cảnh báo dự đoán trên biểu đồ báo rằng phòng sẽ quá nóng nếu không có gì thay đổi."
3. Chuyển nhanh sang chế độ xem 3D.
   > "Trong chế độ xem 3D, bạn có thể thấy người đi vào qua cửa trượt tự động khi số người tăng, và sàn nhà chuyển sang màu đỏ khi phòng nóng lên."

---

## Cảnh 4 — Điều khiển vòng kín: PID hoạt động (2:20 – 3:40)

**Trên màn hình:** Dashboard, hiển thị bảng HVAC và biểu đồ nhiệt độ.

**Thao tác & Thuyết minh:**
1. **Bật điều hòa (AC ON)**, setpoint **22 °C**.
   > "Bây giờ tôi bật điều hòa với nhiệt độ mục tiêu 22 độ. Bộ điều khiển PID tiếp quản: nó đo sai số giữa nhiệt độ phòng và setpoint, rồi điều chỉnh liên tục công suất điều hòa từ 0 đến 100 phần trăm của công suất tối đa 3,5 kilowatt."
2. Quan sát `ac_power_pct` tăng vọt lên ~100 %, rồi nhiệt độ giảm.
   > "Khi sai số lớn, thành phần tỉ lệ (proportional) đẩy điều hòa lên công suất tối đa. Khi nhiệt độ tiến gần setpoint, công suất giảm dần một cách mượt mà thay vì bật/tắt thô kiểu đóng-mở."
3. Đợi đến khi nhiệt độ khóa chặt ở 22 °C với điều hòa chạy ở mức công suất một phần, ổn định.
   > "Và đây là kết quả then chốt: nhiệt độ khóa chính xác ở 22 độ, ngay cả khi có 25 người bên trong. Thành phần tích phân (integral) loại bỏ sai số tĩnh mà một bộ điều khiển tỉ lệ đơn thuần sẽ để lại, còn thành phần vi phân (derivative) dập tắt hiện tượng vọt lố. Cơ chế chống bão hòa (anti-windup) giữ cho bộ điều khiển vẫn phản hồi nhanh ngay cả sau thời gian dài chạy hết công suất."

---

## Cảnh 5 — Vòng phản hồi của Digital Twin (3:40 – 4:30)

**Trên màn hình:** Bảng điều khiển và trạng thái HVAC đặt cạnh nhau.

**Thao tác & Thuyết minh:**
1. Đổi setpoint từ 22 → **25 °C**.
   > "Hãy xem điều gì xảy ra khi tôi đổi setpoint. Dashboard không tự ý giả định giá trị mới — nó phát một lệnh qua MQTT, bộ mô phỏng áp dụng, rồi trạng thái *đã xác nhận* quay về và cập nhật màn hình. Chính vòng khứ hồi đó khiến đây là một digital twin thực sự chứ không phải một 'bóng số' một chiều."
2. Cho thấy công suất điều hòa giảm (phòng đang mát hơn setpoint mới), rồi ổn định ở 25 °C.
   > "Bộ điều khiển lập tức giảm công suất vì phòng giờ đã dưới mục tiêu, rồi hội tụ lại ở setpoint mới."

---

## Cảnh 6 — Chế độ xem phòng 3D (4:30 – 5:20)

**Trên màn hình:** Chế độ xem 3D độc lập tại `http://localhost:8000` (hoặc chế độ xem nhúng, toàn màn hình).

**Thao tác & Thuyết minh:**
1. Xoay camera quanh phòng lab và hành lang.
   > "Chế độ xem 3D được dựng bằng Three.js và đăng ký (subscribe) trực tiếp các topic MQTT ngay từ trình duyệt qua WebSocket — không cần thêm backend nào."
2. Giảm số người xuống **5**; quan sát người đi ra qua cửa trượt.
   > "Khi tôi giảm số người trên dashboard, các nhân vật đi ra qua cửa kính tự động theo thời gian thực."
3. Chỉ vào màu sàn.
   > "Màu sàn mã hóa nhiệt độ — xanh dương khi phòng ở đúng setpoint, và chuyển dần sang đỏ khi nóng lên."

---

## Cảnh 7 — Giao diện lệnh MQTT & Khả năng phục hồi (5:20 – 6:10)

**Trên màn hình:** Terminal đặt cạnh dashboard.

**Thao tác & Thuyết minh:**
1. Phát một lệnh từ terminal:
   ```bash
   docker exec mosquitto mosquitto_pub -t twin/room1/cmd/occupancy -m '{"value": 30}'
   ```
   > "Mọi thứ được điều khiển qua các topic MQTT mở, nên bất kỳ client nào cũng có thể tham gia. Ở đây tôi đặt số người thành 30 thẳng từ dòng lệnh — và cả dashboard lẫn chế độ xem 3D đều phản ứng ngay lập tức."
2. (Tùy chọn) Dừng bộ mô phỏng bằng Ctrl-C; cho thấy dashboard chuyển sang `offline`.
   > "Nếu bộ mô phỏng chết, cơ chế Last Will and Testament của broker lập tức đánh dấu twin là offline trên dashboard. Khi khởi động lại, các message được lưu giữ (retained) sẽ khôi phục trạng thái mới nhất ngay tức thì."
3. Khởi động lại bộ mô phỏng.

---

## Cảnh 8 — Tổng kết (6:10 – 6:40)

**Trên màn hình:** Sơ đồ kiến trúc lần nữa, hoặc dashboard ở trạng thái ổn định tại setpoint.

**Thuyết minh:**
> "Tóm lại: một bộ mô phỏng phòng dựa trên vật lý, giao tiếp MQTT hướng sự kiện với trạng thái lưu giữ và phát hiện sự cố, một dashboard trực tiếp cùng trực quan hóa 3D, và một vòng phản hồi khép kín với bộ điều khiển PID tự điều chỉnh — tất cả hợp thành một digital twin hoàn chỉnh, thời gian thực của một phòng thí nghiệm thông minh. Cảm ơn các bạn đã theo dõi."

---

## Ý tưởng cảnh phụ / B-roll

- Terminal chạy `uv run pytest -v` với toàn bộ unit test pass.
- Cận cảnh các hệ số PID trong `simulator/pid_controller.py` trong khi thuyết minh vai trò của Kp/Ki/Kd.
- Đặt cạnh nhau biểu đồ nhiệt độ trên dashboard và màu sàn 3D trong lúc phòng đang hạ nhiệt.

## Mẹo quay

- Quay ở tốc độ mô phỏng ×10 cho mọi giai đoạn biến đổi nhiệt; cắt bỏ thời gian chết khi dựng.
- Quay Cảnh 3–5 trong một lần liền mạch để lịch sử biểu đồ kể trọn câu chuyện.
- Giữ chuột đứng yên khi thuyết minh; chỉ di chuột để chỉ vào đúng thứ đang được mô tả.
