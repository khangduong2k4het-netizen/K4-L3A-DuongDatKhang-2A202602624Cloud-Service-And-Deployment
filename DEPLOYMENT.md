# Thông tin triển khai — Checkpoint 5

## Học viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Dương Đạt Khang (theo tên repository) |
| Mã học viên | 2A202602624 (theo tên repository) |
| Repo | https://github.com/khangduong2k4het-netizen/K4-L3A-DuongDatKhang-2A202602624Cloud-Service-And-Deployment |

## Trạng thái

Đã kiểm chứng Docker Compose local ngày 28/09/2026.
Đang dùng phương án dự phòng `LOCAL_FALLBACK=true`, CP5 tối đa **9/15**.
Chưa triển khai cloud: phiên làm việc chưa có service/account cloud được cung cấp.
Platform cloud dự kiến: Render (cấu hình `render.yaml` có sẵn);
Railway có cấu hình `railway.toml`. Chưa xác nhận triển khai trên hai nền tảng này.

- Local URL: http://localhost:18000
- Public HTTPS URL: chưa có.
- Agent và Redis đều báo healthy.
- Cổng 8000 đang do dự án khác sử dụng, nên dùng PORT=18000.
- Redis nằm trong mạng Compose, không publish cổng Redis ra host.

## Cấu hình

| Biến | Nguồn / ý nghĩa |
|---|---|
| `PORT` | .env local; cloud cấp khi triển khai |
| `AGENT_API_KEY` | .env bị Git bỏ qua; cloud phải đặt qua secret store |
| `REDIS_URL` | Compose trỏ tới service redis; cloud cần Redis của platform |
| `RATE_LIMIT_PER_MINUTE` | .env hoặc mặc định 10 |
| `MONTHLY_BUDGET_USD` | .env hoặc mặc định 10.0 |
| `LOG_LEVEL` | .env hoặc mặc định INFO |
| `LOCAL_FALLBACK` | true cho phiên kiểm tra local |
| `LOCAL_BASE_URL` | http://localhost:18000 |
| `DEPLOY_API_KEY` | Chỉ cần cho kiểm tra bổ sung trên cloud; không ghi secret vào tài liệu |

## Bằng chứng chạy thật

Build: `docker build -t day12-agent:prod .`.

Docker Desktop hiển thị **252 MB disk usage**, **59.6 MB content size**.
`docker image inspect` trả `Size=59551039` byte cho content trên image store
containerd của máy này. Cả hai số đều dưới **500 MB**; đây là kích thước
runtime image, không phải tổng build cache hay tổng stack Redis + agent.
Script `scripts/check-image-size.ps1` kiểm tra cả hai cách báo dung lượng.

Kiểm tra bên trong image: UID=10001; pytest không được cài; không có /app/.env.

Bộ kiểm thử CP1–CP5 và regression: **83 passed, 5 skipped** (10,51 giây).
Hai test Docker đã build/đo image thật. Năm test cloud được bỏ qua do
LOCAL_FALLBACK=true; các test CP5 local đều pass. Có một cảnh báo deprecation
từ Starlette/httpx trong môi trường kiểm thử, không làm test thất bại.
Bonus CI/CD không nằm trong lần kiểm chứng này.

Kết quả gọi HTTP thật, dùng user kiểm thử riêng:

```text
GET /health 200 {"status":"ok","service":"day12-agent","version":"1.0.0"}
GET /ready 200 {"status":"ready","redis":true}
POST /ask without key 401
POST /ask authenticated statuses [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 429]
history lengths [0, 2]
```

Ảnh chụp trình duyệt headless từ endpoint đang chạy thật:
[screenshots/health.png](screenshots/health.png). Đây là ảnh dịch vụ local,
không phải ảnh dashboard cloud.

## Tái kiểm tra

```powershell
docker compose up -d --wait
docker compose ps
.\scripts\check-image-size.ps1
curl.exe -i http://localhost:18000/health
curl.exe -i http://localhost:18000/ready
.\.venv\Scripts\python.exe -m pytest tests/test_cp5.py -v
```

Lấy khóa từ .env hoặc môi trường trong máy để gọi /ask; không dán khóa vào
tài liệu hoặc screenshot. Test kiểm tra auth ở local được bổ sung bằng phép
gọi thật nêu trên, không dùng mock HTTP.

## Để hoàn tất CP5 cloud

Triển khai service Docker và Redis, đặt các biến môi trường ở secret store,
ghi URL HTTPS thật tại đây, tắt LOCAL_FALLBACK, đặt DEPLOY_API_KEY trong
.env local nếu cần rồi chạy lại tests/test_cp5.py. Bổ sung ảnh dashboard
và kết quả health/readiness cloud. Chưa đánh dấu các bước này đã hoàn tất.

## Giới hạn của mô hình lab

X-User-Id do client cung cấp dưới một API key dùng chung; đây chưa phải hệ
thống định danh đa người dùng. Cost guard kiểm tra chi phí đã ghi trước khi
gọi mock LLM; nó chưa đặt trước ngân sách cho nhiều lượt gọi LLM đồng thời.
Không nên coi đó là bảo đảm cứng cho hóa đơn LLM thật.
