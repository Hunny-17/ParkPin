# ParkPin G1 — Kiểm thử và nghiệm thu

## Delivered code
- 3 Fragments: Home, Save Parking, History
- Bottom Navigation giữ nguyên thanh tab khi chuyển màn
- CTA Home -> Save; shortcut Lịch sử -> History
- Card Tìm xe chỉ hiện thông báo G3, chưa giả lập điều hướng Maps
- WindowInsets cho status bar / navigation bar / keyboard
- Gradle Wrapper v9.6.0, .gitignore, GitHub Actions assembleDebug

## Automated verification (pending)
- [ ] GitHub Actions assembleDebug thành công
- [ ] Clone sạch, Sync Gradle bằng JDK 17 và SDK 37
- [ ] Cài và chạy app trên Emulator

## Manual emulator acceptance (pending)
- [ ] Home mở mặc định, không crash
- [ ] Chuyển Home -> Lưu xe -> Lịch sử -> Home
- [ ] Nút LƯU VỊ TRÍ ĐỖ XE trên Home mở màn Lưu xe
- [ ] Card Lịch sử trên Home mở lịch sử có 3 điểm đỗ mẫu
- [ ] Card Tìm xe không mở bản đồ giả, hiện thông báo G3
- [ ] Cuộn tới cuối tất cả màn không bị Bottom Navigation che
- [ ] Mở bàn phím trên form, vẫn cuộn tới cuối
- [ ] Xoay màn hình ở tab Lịch sử: khôi phục tab được chọn
- [ ] Nhấn Back ở tab phụ: về Home

## Scope lock
Không có GPS, Room/SQLite, lưu xe hay camera trong G1. Form Save và lịch sử đang là dữ liệu mẫu. Không được đánh dấu G1 nghiệm thu nếu chưa có build/test thực tế.
