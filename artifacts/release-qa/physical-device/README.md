# ParkPin — Physical Device Final Acceptance

**PASS 18/18** trên Android 15 / API 35 ngày 25/11/2026 (Asia/Bangkok). Máy `23021RAAEG`, product `tapas_global`, serial `ee8318b9`, ABI `arm64-v8a`. APK debug được build từ `53b510fbbd62738c36c96cf8bc907981bad6f0b1`. SHA-256 trên máy và bản build đều là `B1CD6395F39BA4109169DCE1E282BAB8AC39381A2908F302C304D8F8FA05AFD0`. [Thiết bị](device.txt) · [APK](apk.json) · [Build](build.log) · [Cài đặt](install.log)

| ID | Ca kiểm thử | Verdict | Kết quả thực tế |
|---|---|---|---|
| P01 | Cài đặt và khởi chạy | PASS | ADB cài bản debug, mở MainActivity, SHA-256 APK cài khớp bản build. [Bằng chứng](apk.json) |
| P02 | Navigation ba Fragment | PASS | Home, Lưu xe và Lịch sử đều mở và chọn đúng tab. [Bằng chứng](screenshots/03-history-tab.png) |
| P03 | Validation tên bãi đỗ | PASS | Hiện lỗi bắt buộc và Room vẫn rỗng. [Bằng chứng](screenshots/04-required-name.png) |
| P04 | Lưu vị trí thủ công | PASS | Lưu bản ghi QA với tọa độ NULL. [Bằng chứng](room-manual.json) |
| P05 | GPS khi từ chối quyền | PASS | Chọn Không cho phép. ParkPin hiển thị cách lưu thủ công. [Bằng chứng](screenshots/06-gps-denied.png) |
| P06 | GPS khi cấp quyền | PASS | Android cấp quyền chính xác khi dùng ứng dụng. Fix thật được lưu vào Room. [Bằng chứng](gps.json) |
| P07 | Google Maps nhận đúng tọa độ | PASS | Google Maps lên foreground. URI từ Intent thực tế khớp tọa độ Room đến 7 chữ số thập phân. [Bằng chứng](maps-intent.json) |
| P08 | Photo Picker và preview | PASS | ParkPin gọi PICK_IMAGES thật. Chọn ảnh QA xanh rồi bấm Xong. Đã mở ảnh preview. [Bằng chứng](screenshots/07-green-preview.png) |
| P09 | Room và private storage | PASS | Room lưu photoPath. JPEG riêng 240×144 giải mã đúng mẫu QA. [Bằng chứng](room-photo-saved.json) |
| P10 | Force-stop/restart | PASS | ID, photoPath và bytes JPEG giữ nguyên sau force-stop và mở lại. [Bằng chứng](room-photo-restarted.json) |
| P11 | History hiện đúng ảnh | PASS | Ảnh QA xanh nằm ở đúng hàng đã lưu. [Bằng chứng](screenshots/10-history-photo.png) |
| P12 | Chỉnh sửa vị trí và đổi ảnh | PASS | Giữ cùng ID, cập nhật tầng QA-2, ảnh cam/tím thay ảnh xanh. JPEG cũ biến mất. [Bằng chứng](room-photo-replaced-verified.json) |
| P13 | Bỏ ảnh và lưu | PASS | photoPath về NULL và JPEG cam/tím biến mất. [Bằng chứng](room-photo-removed.json) |
| P14 | Chuyển vị trí active | PASS | Home hiện bản ghi QA đã chọn và Room chỉ có một hàng active. [Bằng chứng](room-active-switched.json) |
| P15 | Xóa bản ghi và dọn file | PASS | Xóa bản ghi còn ảnh qua dialog. Room mất hàng và private storage mất JPEG. [Bằng chứng](room-after-photo-delete.json) |
| P16 | Keyboard, rotation và Back | PASS | Cuộn đến nút Lưu khi IME mở. Xoay ngang rồi dọc giữ tên nháp. Back về Home và không ghi nháp. [Bằng chứng](screenshots/16-keyboard-save.png) |
| P17 | Lưu thủ công offline | PASS | Android báo không có mạng mặc định trước và sau khi lưu. Room có hàng QA mới. [Bằng chứng](offline.json) |
| P18 | Crash và Visual QA | PASS | Crash buffer không có ParkPin. Đã mở và kiểm tra ảnh thực tế Home, form, History, ảnh đổi/bỏ, dialog xóa và xoay. [Bằng chứng](logcat-parkpin.txt) |

Room được đọc từ bản sao DB và WAL khi UI ổn định. Chỉ bản ghi QA đi vào bằng chứng và tọa độ thật được che. Ảnh bằng chứng chỉ chụp ParkPin sau khi đối chiếu ảnh thử theo kích thước và màu. Ảnh bàn phím được cắt tại mép cửa sổ ParkPin để bỏ phần nền bàn phím của Owner. [Room trước ca thử chức năng](room-before.json) · [Room sau dọn](room-final-empty.json) · [Bảng kết quả máy đọc](results.json)

Photo Picker trên máy này có bước Xong. Xác nhận bằng hành động accessibility của UI Automator trên nút hệ thống. Một ảnh nháp không khớp dữ liệu QA trong lần thử đầu đã được bỏ qua nút Bỏ ảnh. Ảnh đó không xuất hiện trong bản ghi, ảnh chụp hay repository. Các lần chạy PASS dùng đúng ảnh QA xanh và cam/tím. [Intent](picker-intent.txt) · [Xác nhận hệ thống](picker-touch-done.txt) · [JPEG xanh](qa-green.jpg) · [JPEG cam](qa-orange.jpg)

Đã xóa tất cả bản ghi thử qua UI và dọn file thử được tạo cho phiên này. Room trở lại rỗng. Đã khôi phục cấu hình Wi-Fi, dữ liệu di động và xoay màn hình. APK debug vẫn cài trên thiết bị.

**Lỗi còn tồn tại.** Không phát hiện lỗi cản thao tác trong P01–P18. Trên máy này, nhãn Đặt hiện tại xuống hai dòng và phần viền dưới của nút bị cắt nhẹ trong History. Nhãn vẫn đọc được và thao tác chuyển active đã PASS. Ghi nhận ở mức hiển thị, không sửa UI trong đợt nghiệm thu này. [Ảnh History](screenshots/10-history-photo.png)

Bước xác nhận Xong là hành vi của trình chọn ảnh hệ thống.
