12 Factor dự án phải tuân theo:

1. Codebase (Mã nguồn): Một codebase duy nhất được theo dõi bằng hệ thống quản lý mã nguồn (như Git), được triển khai cho nhiều môi trường khác nhau.
2. Dependencies (Thư viện phụ thuộc): Khai báo rõ ràng và cô lập tất cả các thư viện, gói phụ thuộc của ứng dụng, không dựa vào các gói có sẵn ở hệ thống ngầm định.
3. Config (Cấu hình): Lưu trữ cấu hình trong biến môi trường thay vì viết cứng (hardcode) trong mã nguồn để dễ dàng thay đổi giữa các môi trường.
4. Backing Services (Dịch vụ hỗ trợ): Xử lý các dịch vụ đi kèm (như cơ sở dữ liệu, bộ nhớ đệm cache, dịch vụ gửi email) như một tài nguyên đính kèm có thể thay thế dễ dàng qua kết nối mạng.
5. Build, release, run (Xây dựng, phát hành, thực thi): Tách biệt hoàn toàn ba giai đoạn: Build (biên dịch mã thành gói), Release (kết hợp gói với cấu hình môi trường), và Run (chạy ứng dụng trên máy chủ).
6. Processes (Tiến trình): Chạy ứng dụng dưới dạng một hoặc nhiều tiến trình không có trạng thái (stateless), dữ liệu cần lưu trữ dài hạn phải đẩy vào backing service như cơ sở dữ liệu.
7. Port Binding (Ràng buộc cổng): Xuất ra dịch vụ của ứng dụng thông qua việc ràng buộc cổng (port binding), tự phục vụ yêu cầu mà không phụ thuộc vào web server bên ngoài nhúng sẵn.
8. Concurrency (Tính đồng thời): Mở rộng quy mô (scale) bằng cách gia tăng số lượng bản sao (process/instance) của tiến trình thay vì nâng cấp phần cứng một máy đơn lẻ.
9. Disposability (Tính hủy diệt): Tối ưu hóa tính ổn định với thời gian khởi động nhanh và tiến trình tắt đi một cách duyên dáng (graceful shutdown) khi có sự cố hoặc cập nhật.
10. Dev/Prod Parity (Đồng bộ môi trường): Giữ cho môi trường phát triển (development), kiểm thử (staging) và sản xuất (production) giống nhau nhất có thể bằng cách rút ngắn thời gian và sự khác biệt.
11. Logs (Nhật ký): Xem logs như là các dòng sự kiện (event streams) và xuất trực tiếp ra luồng chuẩn stdout để các công cụ bên ngoài thu thập, xử lý.
12. Admin Processes (Tiến trình quản trị): Chạy các tác vụ quản trị hoặc bảo trì (như chạy migration database) dưới dạng các tiến trình độc lập cùng môi trường với ứng dụng chính.

Lưu ý, không được lộ api_key. Giới hạn rate limi
