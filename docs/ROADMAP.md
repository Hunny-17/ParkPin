# ParkPin — Roadmap MVP 14 ngày

> Đây là **kế hoạch**. Không đánh dấu những tính năng chưa được hiện thực hóa như đã hoàn thành.

## Phạm vi
Ứng dụng Android Native hỗ trợ ghi nhớ vị trí đỗ xe và mở điều hướng quay lại. Java + XML, Room/SQLite, Fused Location Provider, Google Maps Intent. Hoạt động offline cho lưu trữ dữ liệu; không có đăng nhập hoặc backend.

## Milestone

| Mốc | Dự kiến | Công việc chính | Trạng thái |
|---|---|---|---|
| `v0.1.1-ui` | Baseline | Home UI tĩnh, các màn Save/History ở XML preview, AGP 9.4.0 | UI Home đã được người dùng chạy và xác nhận trên Emulator API 37.2 |
| `v0.2.0` | Ngày 2–3 | Tạo 3 Fragments, Bottom Navigation hoạt động, sửa cuộn/keyboard | QA 23/11/2026: build sạch JDK 17, Emulator 9/9, Visual/Crash PASS; CI HEAD nghiệm thu xem PR #1 |
| `v0.3.0` | Ngày 4–6 | Room, ParkingEntity/Dao/Repository, tạo/xem/sửa/xóa và lịch sử | Chưa thực hiện |
| `v0.4.0` | Ngày 7–10 | Runtime permission, lấy GPS, lưu lat/lng, mở Google Maps | Chưa thực hiện |
| `v0.5.0` | Ngày 11–12 | Photo Picker, ảnh điểm đỗ, trạng thái rỗng/lỗi | Chưa thực hiện |
| `v1.0.0` | Ngày 13–14 | Kiểm thử hồi quy, sửa lỗi, tài liệu, APK nộp môn | Chưa thực hiện |

## Điều kiện nghiệm thu từng giai đoạn

### UI & Navigation
- [x] Home UI render trên Emulator (đã được người dùng xác nhận).
- [x] Điều hướng 3 Fragments đã kiểm thử trên Emulator.
- [x] Cuộn và IME insets đã kiểm thử; sửa lỗi thanh tab cộng lặp insets.
- [x] GitHub Actions assembleDebug HEAD đầu vào thành công; CI commit nghiệm thu xem PR #1.
- [x] Emulator 9/9 và Visual/Crash QA PASS theo [G1_ACCEPTANCE.md](G1_ACCEPTANCE.md), ngày 23/11/2026.

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
- Nghiệm thu G1 ngày 23/11/2026 bổ sung build log JDK 17, ảnh và kết quả thao tác Emulator trong `artifacts/g1/`.

## G1 branch
Feature: `feat/g1-navigation-fragments-wrapper`. Nhánh `main` giữ nguyên tới khi người dùng merge. Local QA G1 PASS; Ready to Merge phụ thuộc CI HEAD nghiệm thu mới, được ghi tại [PR #1](https://github.com/Hunny-17/ParkPin/pull/1). Chưa triển khai G2/G3.
