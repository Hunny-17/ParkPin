# ParkPin — Android Native

Ứng dụng ghi nhớ nơi đỗ xe. G1 Navigation và G2 Room + CRUD đã tích hợp vào `main`. G3 trên branch riêng đang thêm GPS tùy chọn và Google Maps Intent; camera thuộc G4. GPS không bắt buộc để lưu vị trí thủ công.

## Tech stack
- Java 17 + XML + AndroidX AppCompat/Fragment
- Room 2.8.5, lưu trữ offline, repository bất đồng bộ và migration v1→v2 không mất dữ liệu
- Google Play services location 21.4.0 cho GPS một lần khi người dùng yêu cầu (G3 Draft)
- AGP 9.4.0, Gradle Wrapper 9.6.0
- Compile/Target SDK 37, Min SDK 24
- Package `com.tranquochuy.parkpin`

## Chạy trên Android Studio
Clone repository, mở thư mục gốc ParkPin bằng Android Studio. Chọn Gradle JDK 17, cài SDK Platform 37, Sync và Run.

```bat
gradlew.bat :app:assembleDebug
```

macOS/Linux: `./gradlew :app:assembleDebug`.

Wrapper scripts/JAR được lấy từ nguồn chính thức `gradle/gradle` tag `v9.6.0`.

## G1 đã triển khai
- `MainActivity` có Fragment container và Bottom Navigation cố định.
- `HomeFragment`: CTA Lưu xe, shortcut Lịch sử, thông báo chưa có tìm xe.
- G1 ban đầu có form Save và History mẫu; G2 đã thay bằng Room và dữ liệu thực trên thiết bị.
- Giữ lựa chọn tab khi xoay màn hình, xử lý Back từ tab phụ về Home.
- Insets cho màn hình edge-to-edge và bàn phím, mỗi màn cuộn độc lập.
- `.gitignore` và Android CI build `assembleDebug`.

## G3 đang triển khai (Draft / QA chưa chạy)
- Quyền coarse/fine location chỉ yêu cầu khi nhấn **LẤY GPS**; từ chối vẫn lưu thủ công.
- GPS lưu tùy chọn vào Room và không được dùng để thay thông tin tầng/khu/cột.
- Nếu có GPS, **Tìm xe** mở app Maps bên ngoài; không có app Maps sẽ thông báo phù hợp.
- [Kế hoạch và cổng nghiệm thu G3](docs/G3_PROGRESS.md); **không tuyên bố G3 PASS** trước khi chạy kiểm thử thực tế.

## Trạng thái / tài liệu
- [Roadmap MVP 14 ngày](docs/ROADMAP.md)
- [Checklist nghiệm thu G1](docs/G1_ACCEPTANCE.md)
- [Nghiệm thu G2](docs/G2_ACCEPTANCE.md): clean build PASS, JVM 1/1, instrumentation 5/5, CRUD 10/10 và hồi quy 6/6 trên Emulator ngày 23/11/2026. [Bằng chứng](artifacts/g2/). G2 đã merge ngày 23/11/2026; G3 đang triển khai và phải được kiểm thử riêng.

**QA G1 ngày 23/11/2026:** Build sạch JDK 17 PASS; Emulator API 37.2 **9/9 PASS**; Visual và Crash/Regression PASS. Đã sửa lỗi Bottom Navigation cộng lặp keyboard insets. [`artifacts/g1/`](artifacts/g1/) có ảnh thật, build log và script ADB chạy lại. CI commit nghiệm thu và trạng thái Ready for Review được cập nhật trên [PR #1](https://github.com/Hunny-17/ParkPin/pull/1) sau push; chỉ merge khi CI HEAD mới SUCCESS.
