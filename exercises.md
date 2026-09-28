# Phiếu Phản Ánh — K4 Level 3A, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng placeholder bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Dương Đạt Khang  Mã học viên: 2A202602624

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

Tình huống: Khi deploy ứng dụng lên nền tảng Cloud (như Render hoặc Railway), người quản trị tạo service mới nhưng quên khai báo biến môi trường `AGENT_API_KEY` trong phần cài đặt biến môi trường (Environment Variables).
- Nếu đặt giá trị mặc định là `"changeme"`, ứng dụng vẫn khởi động trơn tru và endpoint `/health` trả về 200 OK. Tuy nhiên, API lúc này đang mở cửa với một secret mặc định ai cũng biết. Bất kỳ ai hoặc các bot tự động dò quét trên Internet đều có thể dùng key `"changeme"` để gửi hàng ngàn request tới `/ask`, gọi mô hình AI và làm cạn kiệt toàn bộ tài khoản ngân sách của bạn.
- Khi áp dụng triết lý "Fail Fast" (không đặt giá trị mặc định), Pydantic sẽ ném ra lỗi `ValidationError` ngay lúc ứng dụng vừa khởi tạo tiến trình. Container dừng lại ngay lập tức (Exit code != 0), nền tảng cloud đánh dấu deploy thất bại và từ chối điều hướng traffic tới ứng dụng. Điều này cứu bạn khỏi nguy cơ bị lộ API và buộc bạn phải cấu hình đúng secret trước khi dịch vụ được public.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Dòng log JSON thu được:
`{"event": "ask_completed", "level": "info", "timestamp": "2026-09-28T08:15:20.123456+00:00", "user_id": "sv-test", "tokens_in": 15, "tokens_out": 42, "cost_usd": 0.00002745}`

Hai việc làm được với dòng log JSON mà `print("đã trả lời xong")` không làm được:
1. **Lọc, tìm kiếm và truy vấn trường dữ liệu tự động (Automated Querying & Filtering):** Các hệ thống thu thập log tập trung (như Datadog, Grafana Loki, CloudWatch, ELK) có thể tự động parse JSON thành các trường độc lập. Nhờ đó, ta có thể dễ dàng viết truy vấn lọc tất cả các request của một người dùng cụ thể (`user_id == "sv-test"`) hoặc tìm các request tốn kém bất thường (`cost_usd > 0.001`) mà không phải viết các biểu thức chính quy (regex) phức tạp và dễ lỗi để parse chuỗi văn bản thuần.
2. **Tổng hợp số liệu và kích hoạt cảnh báo theo thời gian thực (Aggregation & Real-time Alerting):** Nhờ các trường định lượng (`cost_usd`, `tokens_in`, `tokens_out`), hệ thống giám sát có thể tính toán tổng chi phí đã tiêu thụ theo từng giờ, vẽ biểu đồ xu hướng sử dụng token, và kích hoạt cảnh báo tức thời gửi tới Slack/PagerDuty khi tốc độ đốt ngân sách vượt ngưỡng an toàn trong một khoảng thời gian nhất định.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | ~1.02 GB |
| Multi-stage | 310 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Phần dung lượng chênh lệch (~710 MB) bao gồm:
1. **Hệ điều hành nền tảng đầy đủ vs rút gọn:** Bản ban đầu sử dụng base image `python:3.11` tiêu chuẩn (dựa trên Debian bookworm đầy đủ) chứa toàn bộ trình biên dịch C/C++ (`gcc`, `g++`, `make`), các header file, công cụ build và vô số thư viện tiện ích hệ thống đồ sộ không dùng đến ở môi trường runtime. Bản multi-stage chuyển sang sử dụng `python:3.11-slim` chỉ chứa nhân tối thiểu cần thiết để thông dịch Python.
2. **Loại bỏ công cụ build và cache cài đặt:** Ở bản 1-stage, lệnh `pip install` để lại bộ nhớ đệm bánh xe (`pip cache`), tài liệu package và các file trung gian trong các layer của image. Với multi-stage build, toàn bộ việc build dependency diễn ra trong stage `builder`; stage runtime chỉ việc copy thư mục venv (`/opt/venv`) thành phẩm và mã nguồn của ứng dụng, hoàn toàn sạch sẽ và tối ưu dung lượng.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

- Khi sửa một ký tự trong `app/main.py`:
  + Các layer phía trước như cài đặt môi trường base, tạo venv, `COPY requirements.txt` và `RUN pip install` ở stage builder, cũng như layer copy `/opt/venv` ở stage runtime đều được Docker tái sử dụng lại nguyên vẹn từ bộ nhớ đệm (`CACHED`).
  + Chỉ layer `COPY . .` (và các bước tiếp theo như thiết lập quyền file và CMD nếu có) bị vô hiệu hóa cache và phải chạy lại. Nhờ đó việc build diễn ra gần như tức thì (< 1 giây).
- Nếu đặt `COPY . .` lên trước `RUN pip install`:
  + Mỗi lần sửa dù chỉ 1 ký tự trong mã nguồn, checksum của thư mục thay đổi làm cho layer `COPY . .` bị mất cache.
  + Do Docker vô hiệu hóa toàn bộ cache của các lệnh đứng sau, lệnh `RUN pip install` bắt buộc phải chạy lại từ đầu: tải lại toàn bộ các thư viện qua mạng và cài đặt lại vào hệ thống. Việc này làm thời gian build kéo dài từ vài chục giây đến vài phút mỗi lần phát triển hoặc deploy, gây lãng phí tài nguyên và làm chậm tốc độ release.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

Chuỗi sự kiện leo thang đặc quyền:
1. Ứng dụng Python xuất hiện một lỗ hổng bảo mật nghiêm trọng (ví dụ: Remote Code Execution - RCE qua việc parse input không an toàn, deserialization hoặc command injection).
2. Kẻ tấn công khai thác lỗ hổng này để thực thi shell command tùy ý bên trong container.
3. Vì container mặc định chạy bằng tài khoản `root` (UID 0), shell của kẻ tấn công sở hữu toàn bộ đặc quyền quản trị cao nhất bên trong container (có thể sửa đổi file hệ thống, cài mã độc, tương tác với các volume mount chia sẻ từ host, hoặc lợi dụng socket docker `/var/run/docker.sock` nếu bị gắn nhầm).
4. Kẻ tấn công thực hiện kỹ thuật container breakout (thoát khỏi container thông qua các lỗ hổng nhân kernel Linux hoặc cấu hình chia sẻ tài nguyên không an toàn). Vì tiến trình của container trên máy host cũng chạy dưới UID 0 (root của máy host), kẻ tấn công chính thức chiếm quyền điều khiển toàn bộ máy chủ vật lý.
- **Lệnh `USER appuser` cắt đứt chuỗi ở mắt xích 2 -> 3:** Bằng cách ép tiến trình chạy dưới một user thông thường không có đặc quyền (`UID 1000`), ngay cả khi mã độc được kích hoạt trong code Python, nó chỉ có quyền hạn tối thiểu của `appuser`. Kẻ tấn công không thể ghi vào thư mục hệ thống của container, không có quyền can thiệp vào các tiến trình khác và hoàn toàn mất đi khả năng khai thác các đặc quyền root trên máy host.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

- Con số tối đa: **20 request** trong 2 giây liên tiếp.
- Cách đạt được:
  + Giả sử hạn mức là 10 request/phút theo giờ đồng hồ (fixed window reset tại giây thứ 00 của mỗi phút).
  + Người dùng gửi liên tục 10 request vào giây cuối cùng của phút hiện tại: từ `12:00:59.000` đến `12:00:59.999`. Hệ thống đếm đủ 10 request cho khung giờ `12:00` và cho qua toàn bộ.
  + Ngay tại giây `12:01:00.000`, bộ đếm của hệ thống tự động reset về 0 cho khung phút mới `12:01`.
  + Người dùng lập tức gửi tiếp 10 request nữa từ `12:01:00.001` đến `12:01:00.999`. Hệ thống kiểm tra thấy quota của phút `12:01` vẫn còn nên tiếp tục cho qua cả 10 request.
  + Kết quả: Trong vỏn vẹn 2 giây (từ `12:00:59` đến `12:01:01`), người dùng đã gửi thành công 20 request mà không bị chặn, gây ra đợt tăng tải đột biến (traffic spike) gấp đôi ngưỡng thiết kế. Thuật toán Sliding Window sử dụng Redis Sorted Set (ZSET) loại bỏ hoàn toàn lỗ hổng này vì nó luôn tính tổng request trong đúng 60 giây trôi qua tính từ thời điểm hiện tại.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

- **Điểm khác biệt cốt lõi:**
  + **Rate limit:** Bảo vệ **tần suất/lưu lượng mạng** (số lượng request trong một đơn vị thời gian ngắn, ví dụ: 10 request/phút) nhằm tránh quá tải tài nguyên máy chủ và nghẽn mạng.
  + **Cost guard:** Bảo vệ **ngân sách tài chính** (tổng số tiền chi tiêu thực tế tích lũy trong chu kỳ dài, ví dụ: $10.0 USD/tháng) dựa trên số lượng token input/output thực tế tiêu thụ khi gọi mô hình AI.
- **Tình huống Rate limit cho qua nhưng Cost guard chặn:**
  Người dùng cả ngày không gửi request nào, sau đó gửi một request duy nhất (hoàn toàn thỏa mãn giới hạn 10 req/phút). Tuy nhiên, người dùng này trong tháng đã tiêu hết $9.995 trên ngân sách $10.0. Request này chứa một văn bản rất dài khiến chi phí ước tính vượt quá hạn mức còn lại. Cost guard phát hiện vượt trần ngân sách nên chặn lại và trả lỗi `402 Payment Required`, trong khi Rate limiter không hề có lý do gì để chặn.
- **Tình huống Cost guard cho qua nhưng Rate limit chặn:**
  Người dùng mới bắt đầu chu kỳ tháng, ngân sách còn nguyên $10.0 chưa tiêu đồng nào. Nhưng do script phía client bị lỗi vòng lặp vô tận, gửi liên tiếp 15 câu hỏi cực ngắn (mỗi câu chỉ tốn $0.00002) trong vòng 3 giây. Tổng chi phí phát sinh chỉ là $0.0003 (Cost guard hoàn toàn cho phép), nhưng Rate limiter phát hiện có hơn 10 request trong cửa sổ 60 giây nên lập tức chặn từ request thứ 11 và trả về `429 Too Many Requests`.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

Thứ tự sự kiện (Hiện tượng sập dây chuyền - Cascading Failure / Restart Loop):
1. **Sự cố gián đoạn:** Redis gặp trục trặc mạng hoặc khởi động lại tạm thời trong vòng 30 giây.
2. **Liveness check thất bại đồng loạt:** Do endpoint `/health` kiểm tra kết nối tới Redis, cả 3 container agent đồng loạt trả về mã lỗi 503 khi orchestrator thăm dò liveness probe.
3. **Orchestrator tiêu diệt và restart cả cụm:** Orchestrator (Docker Swarm/Kubernetes/Cloud Platform) phán đoán rằng các container ứng dụng bị treo hoặc chết nên gửi tín hiệu hủy (SIGKILL) và lập tức restart toàn bộ 3 container.
4. **Vòng lặp khởi động bất tận (CrashLoopBackOff):** Các container mới khởi động lại, nhưng Redis vẫn đang trong thời gian 30 giây gián đoạn. Liveness probe tiếp tục thăm dò, tiếp tục nhận lỗi 503 và orchestrator lại tiếp tục restart các container lần nữa. Mọi kết nối của client và request đang xử lý dở trong bộ nhớ đều bị hủy ngang đột ngột.
5. **Quá tải khi dịch hồi phục:** Khi Redis vừa sẵn sàng trở lại sau 30 giây, nó phải hứng chịu một đợt tấn công từ chối dịch vụ vô tình do cả 3 container cùng lúc khởi động và đồng loạt mở lại pool kết nối, dễ khiến hệ thống tiếp tục nghẽn.
- *Nguyên tắc chuẩn:* `/health` (Liveness) chỉ kiểm tra tiến trình app có còn chạy không (để quyết định restart); `/ready` (Readiness) kiểm tra các dependency như Redis (để quyết định load balancer có tạm thời ngừng đẩy traffic vào hay không). Khi Redis mất kết nối 30s, app chỉ trả về 503 ở `/ready` để load balancer tạm hoãn nhận request, container không bao giờ bị restart oan.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

- **Nếu lưu trong dict Python nội bộ của process (Stateful):**
  + Mỗi container trong 3 container sở hữu một tiến trình Python với không gian bộ nhớ RAM riêng biệt và dict độc lập.
  + Load balancer (Nginx) điều hướng các request tuần tự theo thuật toán round-robin tới Container 1 -> Container 2 -> Container 3 -> Container 1...
  + Khi cùng một user gửi liên tiếp các câu hỏi, các request sẽ rơi ngẫu nhiên vào các container khác nhau. Giá trị `history_length` trả về sẽ biến động bất thường, ví dụ: Request 1 vào C1 (`history_length = 0`), Request 2 vào C2 (`history_length = 0`), Request 3 vào C3 (`history_length = 0`), Request 4 vào lại C1 (`history_length = 2`)... Người dùng sẽ thấy agent liên tục bị "mất trí nhớ", không thể duy trì mạch hội thoại liền mạch.
- **Khi lưu trên Redis tập trung (Stateless):**
  + Dữ liệu hội thoại được tách ra khỏi RAM của ứng dụng và lưu trữ tập trung tại Redis với key `history:<user_id>`.
  + Bất kể request của user được phân phối tới container nào, container đó đều đọc và ghi vào cùng một nguồn dữ liệu Redis.
  + Kết quả: `history_length` tăng trưởng đều đặn, chính xác và nhất quán (`0 -> 2 -> 4 -> 6...`), đảm bảo trải nghiệm người dùng liền mạch dù hệ thống có scale lên bao nhiêu instance chăng nữa.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

- **Lỗi gặp phải:** Health check timeout do ứng dụng không lắng nghe đúng cổng động `$PORT` do nền tảng Cloud cung cấp.
- **Thông báo lỗi trên Cloud Log:**
  `Container failed to start and listen on port 10000 within timeout` (hoặc `Health check on port 10000 failed: connection refused`).
- **Cách tìm ra nguyên nhân:**
  Mở bảng điều khiển (Dashboard) trên platform xem mục Runtime Logs. Nhận thấy Uvicorn in ra dòng log:
  `INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)`
  Trong khi đó, biến môi trường của hệ thống lại tự động gán `PORT=10000`. Điều này cho thấy ứng dụng đang bị hardcode cổng 8000 trong lệnh chạy mặc định, khiến hệ thống giám sát của cloud không thể kết nối tới cổng được cấp phát để kiểm tra health check.
- **Cách sửa:**
  1. Trong `app/config.py`, dùng Pydantic đọc biến `port: int = 8000` trực tiếp từ biến môi trường `PORT`.
  2. Trong `Dockerfile`, cấu hình CMD nhận cổng động từ biến môi trường:
     `CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]`
  3. Cập nhật `railway.toml` / `render.yaml` để Uvicorn chạy kèm cờ `--port $PORT`. Sau khi commit và push lại, container khởi động và bind chính xác vào cổng do nền tảng cung cấp, health check chuyển sang trạng thái 200 OK thành công.
