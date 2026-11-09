# ParkPin — Android Native

Ứng dụng ghi nhớ nơi đỗ xe. G1 triển khai **Navigation + 3 Fragments**; GPS, Room, Google Maps và Camera thuộc các giai đoạn sau. Tất cả vị trí hiện tại trên Home/History chỉ là dữ liệu mẫu.

## Tech stack
- Java 17 + XML + AndroidX AppCompat/Fragment
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
- `SaveParkingFragment`: form XML hiện có, chưa lưu.
- `HistoryFragment`: 3 vị trí minh họa, chưa có database.
- Giữ lựa chọn tab khi xoay màn hình, xử lý Back từ tab phụ về Home.
- Insets cho màn hình edge-to-edge và bàn phím, mỗi màn cuộn độc lập.
- `.gitignore` và Android CI build `assembleDebug`.

## Trạng thái / tài liệu
- [Roadmap MVP 14 ngày](docs/ROADMAP.md)
- [Checklist nghiệm thu G1](docs/G1_ACCEPTANCE.md)

**Chưa tuyên bố G1 nghiệm thu:** Cần CI build và kiểm tra trên Emulator trước khi merge PR.
