# ParkPin — Android Native

Ứng dụng ghi nhớ nơi đỗ xe. G2 triển khai **Room + CRUD lưu vị trí trên thiết bị**, dựa trên Navigation + 3 Fragments của G1. Home và History đọc dữ liệu đã lưu; GPS, Google Maps và Camera thuộc các giai đoạn sau.

## Tech stack
- Java 17 + XML + AndroidX AppCompat/Fragment
- Room 2.8.5, lưu trữ offline và repository bất đồng bộ
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

## Trạng thái / tài liệu
- [Roadmap MVP 14 ngày](docs/ROADMAP.md)
- [Checklist nghiệm thu G1](docs/G1_ACCEPTANCE.md)
- [Nghiệm thu G2](docs/G2_ACCEPTANCE.md): clean build PASS, JVM 1/1, instrumentation 5/5, CRUD 10/10 và hồi quy 6/6 trên Emulator ngày 23/11/2026. [Bằng chứng](artifacts/g2/). CI final HEAD và trạng thái Ready for Review xem [PR #2](https://github.com/Hunny-17/ParkPin/pull/2); không tự merge.

**QA G1 ngày 23/11/2026:** Build sạch JDK 17 PASS; Emulator API 37.2 **9/9 PASS**; Visual và Crash/Regression PASS. Đã sửa lỗi Bottom Navigation cộng lặp keyboard insets. [`artifacts/g1/`](artifacts/g1/) có ảnh thật, build log và script ADB chạy lại. CI commit nghiệm thu và trạng thái Ready for Review được cập nhật trên [PR #1](https://github.com/Hunny-17/ParkPin/pull/1) sau push; chỉ merge khi CI HEAD mới SUCCESS.
