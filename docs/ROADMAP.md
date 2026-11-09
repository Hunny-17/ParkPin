# ParkPin — Roadmap MVP 14 ngày

> Đây là **kế hoạch**. Không đánh dấu những tính năng chưa được hiện thực hóa như đã hoàn thành.

## Phạm vi
Ứng dụng Android Native hỗ trợ ghi nhớ vị trí đỗ xe và mở điều hướng quay lại. Java + XML, Room/SQLite, Fused Location Provider, Google Maps Intent. Hoạt động offline cho lưu trữ dữ liệu; không có đăng nhập hoặc backend.

## Milestone

| Mốc | Dự kiến | Công việc chính | Trạng thái |
|---|---|---|---|
| `v0.1.1-ui` | Baseline | Home UI tĩnh, các màn Save/History ở XML preview, AGP 9.4.0 | UI Home đã được người dùng chạy và xác nhận trên Emulator API 37.2 |
| `v0.2.0` | Ngày 2–3 | Tạo 3 Fragments, Bottom Navigation hoạt động, sửa cuộn/keyboard | Chưa thực hiện |
| `v0.3.0` | Ngày 4–6 | Room, ParkingEntity/Dao/Repository, tạo/xem/sửa/xóa và lịch sử | Chưa thực hiện |
| `v0.4.0` | Ngày 7–10 | Runtime permission, lấy GPS, lưu lat/lng, mở Google Maps | Chưa thực hiện |
| `v0.5.0` | Ngày 11–12 | Photo Picker, ảnh điểm đỗ, trạng thái rỗng/lỗi | Chưa thực hiện |
| `v1.0.0` | Ngày 13–14 | Kiểm thử hồi quy, sửa lỗi, tài liệu, APK nộp môn | Chưa thực hiện |

## Điều kiện nghiệm thu từng giai đoạn

### UI & Navigation
- [x] Home UI render trên Emulator (đã được người dùng xác nhận).
- [ ] Chuyển Home / Lưu xe / Lịch sử không crash.
- [ ] Nội dung cuộn không bị bottom bar che.

### Local CRUD
- [ ] Lưu vị trí bãi xe, tầng, khu, cột, ghi chú.
- [ ] Thông tin được giữ sau khi đóng app và mở lại.
- [ ] Chỉ một điểm đỗ đang hoạt động; điểm cũ vào lịch sử.
- [ ] Sửa/xóa điểm đỗ hợp lệ.

### GPS & tìm đường
- [ ] Xin quyền khi cần; từ chối quyền vẫn lưu thủ công.
- [ ] Có thể lưu tọa độ nếu dịch vụ vị trí khả dụng.
- [ ] Mở Maps đúng tọa độ đã lưu và xử lý thiếu app bản đồ.

### Ảnh & release
- [ ] Chọn ảnh và lưu tham chiếu bền vững.
- [ ] Chạy thử trên emulator và thiết bị thật (nếu có).
- [ ] Build APK, README, demo và báo cáo.

## Ngoài phạm vi MVP
Không thêm đăng nhập, Firebase, AI, bản đồ nhúng, hệ thống đặt bãi xe, theo dõi xe thời gian thực hoặc thanh toán.

## Lưu ý về baseline
- Source snapshot này xuất phát từ file `ParkPin_UI_Starter_AGP_9.4.0.zip` đã gửi trong cuộc trò chuyện; **không tự động đồng bộ** các chỉnh sửa nếu bạn đã thay đổi code trên máy.
- Bản ZIP nguồn chưa có `gradle-wrapper.jar`. Nếu cần khôi phục wrapper, xem README.
- Chưa có chứng cứ build APK trong môi trường đóng gói; đã có ảnh người dùng chạy UI Home thành công trên emulator.
