# ParkPin — Roadmap MVP 14 ngày

> Đây là **kế hoạch**. Không đánh dấu những tính năng chưa được hiện thực hóa như đã hoàn thành.

## Phạm vi
Ứng dụng Android Native hỗ trợ ghi nhớ vị trí đỗ xe và mở điều hướng quay lại. Java + XML, Room/SQLite, Fused Location Provider, Google Maps Intent. Hoạt động offline cho lưu trữ dữ liệu; không có đăng nhập hoặc backend.

## Milestone

| Mốc | Dự kiến | Công việc chính | Trạng thái |
|---|---|---|---|
| `v0.1.1-ui` | Baseline | Home UI tĩnh, các màn Save/History ở XML preview, AGP 9.4.0 | UI Home đã được người dùng chạy và xác nhận trên Emulator API 37.2 |
| `v0.2.0` | Ngày 2–3 | Tạo 3 Fragments, Bottom Navigation hoạt động, sửa cuộn/keyboard | QA 23/11/2026: build sạch JDK 17, Emulator 9/9, Visual/Crash PASS; CI HEAD nghiệm thu xem PR #1 |
| `v0.3.0` | Ngày 4–6 | Room, ParkingEntity/Dao/Repository, tạo/xem/sửa/xóa và lịch sử | G2 QA 23/11/2026: JVM 1/1, instrumentation 5/5, CRUD 10/10, hồi quy 6/6 PASS; CI final HEAD xem PR #2 |
| `v0.4.0` | Ngày 7–10 | Runtime permission, lấy GPS, lưu lat/lng, mở Google Maps | G3 QA 23/11/2026: JVM 4/4, instrumentation 7/7, quyền 7/7, migration APK thật PASS, persistence 8/8, Maps Intent 9/9, hồi quy PASS; CI HEAD cuối xem PR #3 |
| `v0.5.0` | Ngày 11–12 | Photo Picker, ảnh điểm đỗ, trạng thái rỗng/lỗi | G4 trên codex/g4-photo-picker: JVM 4/4, instrumentation 16/16, UI ảnh/GPS/Maps 16/16, migration APK thật và hồi quy PASS; xem G4_ACCEPTANCE.md |
| `v1.0.0` | Ngày 13–14 | Kiểm thử hồi quy, sửa lỗi, tài liệu, APK nộp môn | Chưa thực hiện |

## Điều kiện nghiệm thu từng giai đoạn

### UI & Navigation
- [x] Home UI render trên Emulator (đã được người dùng xác nhận).
- [x] Điều hướng 3 Fragments đã kiểm thử trên Emulator.
- [x] Cuộn và IME insets đã kiểm thử; sửa lỗi thanh tab cộng lặp insets.
- [x] GitHub Actions assembleDebug HEAD đầu vào thành công; CI commit nghiệm thu xem PR #1.
- [x] Emulator 9/9 và Visual/Crash QA PASS theo [G1_ACCEPTANCE.md](G1_ACCEPTANCE.md), ngày 23/11/2026.

### Local CRUD
- [x] Lưu vị trí bãi xe, tầng, khu, cột, ghi chú.
- [x] Thông tin được giữ sau force-stop và mở lại (đã kiểm thử Emulator).
- [x] Chỉ một điểm đỗ đang hoạt động; điểm cũ vào lịch sử.
- [x] Sửa/xóa điểm đỗ hợp lệ, có dialog xác nhận xóa; xem [G2_ACCEPTANCE.md](G2_ACCEPTANCE.md).

### GPS & tìm đường
- [x] Xin quyền khi cần; từ chối quyền vẫn lưu thủ công — GPS permissions 7/7.
- [x] Có thể lưu tọa độ nếu dịch vụ vị trí khả dụng — GPS persistence 8/8 và migration v1→v2 thực tế PASS.
- [x] Mở Maps đúng tọa độ đã lưu và xử lý thiếu app bản đồ — Maps Intent 9/9, generic fallback qua QA receiver; xem [G3_ACCEPTANCE.md](G3_ACCEPTANCE.md).

### Ảnh & release
- [x] Chọn ảnh, lưu JPEG riêng và photoPath bền vững; thay/bỏ/xóa ảnh dọn đúng file, xem [G4_ACCEPTANCE.md](G4_ACCEPTANCE.md).
- [ ] Chạy thử trên emulator và thiết bị thật (nếu có).
- [ ] Build APK, README, demo và báo cáo.

## Ngoài phạm vi MVP
Không thêm đăng nhập, Firebase, AI, bản đồ nhúng, hệ thống đặt bãi xe, theo dõi xe thời gian thực hoặc thanh toán.

## Lưu ý về baseline
- Source snapshot này xuất phát từ file `ParkPin_UI_Starter_AGP_9.4.0.zip` đã gửi trong cuộc trò chuyện; **không tự động đồng bộ** các chỉnh sửa nếu bạn đã thay đổi code trên máy.
- Bản ZIP nguồn chưa có `gradle-wrapper.jar`. Nếu cần khôi phục wrapper, xem README.
- Nghiệm thu G1 ngày 23/11/2026 bổ sung build log JDK 17, ảnh và kết quả thao tác Emulator trong `artifacts/g1/`.

## Mốc tích hợp
G1, G2 và G3 đã merge qua PR #1, #2, #3 vào `main` ngày 23/11/2026. Merge SHA G3 `44aac930382d87bec3f8bd6c08aa83bdc25fc2f2`; [CI main SUCCESS](https://github.com/Hunny-17/ParkPin/actions/runs/45159706681). G4 triển khai riêng tại `codex/g4-photo-picker` dựa trên main này.

[G3 đã nghiệm thu Emulator](G3_ACCEPTANCE.md) và merge theo chỉ thị tiếp theo của người dùng. [G4 đã nghiệm thu local](G4_ACCEPTANCE.md), chờ review/CI HEAD cuối trên PR riêng; không tự merge G4 hoặc mở rộng sang release/G5.
