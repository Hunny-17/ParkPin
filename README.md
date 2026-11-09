# ParkPin — Android Native UI Starter (v0.1.1, AGP 9.4.0)

Giao diện **Android Studio Java + XML** dành cho đề tài **Ứng dụng ghi nhớ và tìm lại vị trí đỗ xe**.
Đây là UI-only: **không** kết nối GPS, Room/Firebase, camera hay Google Maps; **không** có click listeners / sự kiện nghiệp vụ.
Toàn bộ địa điểm, giờ, lịch sử hiện ra là **dữ liệu minh hoạ**, không phải vị trí thật.

## Môi trường và công nghệ

- Android Studio hỗ trợ **AGP 9.4.0** (ví dụ Rabbit 1 / Quail 4). Không cần nâng Android Studio để chạy bản UI này.
- Android Gradle Plugin: **9.4.0**
- Gradle: **9.6.0** (theo yêu cầu tối thiểu của AGP 9.4)
- JDK: **17+** (khuyên dùng JDK 17 qua Gradle JDK trong Android Studio)
- `compileSdk 37`, `targetSdk 37`, `minSdk 24`
- **Java + XML**, Material Components **1.14.0**, AppCompat **1.8.0**
- Package: `com.tranquochuy.parkpin`

## Xem nhanh concept

File `ui-preview.html` có bản xem nhanh 3 màn hình bằng trình duyệt (đây là concept minh họa, không phải ảnh chụp từ APK).

## Các file giao diện

| File | Ý nghĩa |
| --- | --- |
| `app/src/main/res/layout/activity_main.xml` | Root + bottom navigation minh hoạ |
| `app/src/main/res/layout/screen_home.xml` | **Màn trang chủ** — chạy khi mở app |
| `app/src/main/res/layout/screen_save_parking.xml` | **Màn lưu vị trí** — xem bằng XML Design Preview |
| `app/src/main/res/layout/screen_history.xml` | **Màn lịch sử** — xem bằng XML Design Preview |
| `app/src/main/java/com/tranquochuy/parkpin/MainActivity.java` | Chỉ inflate layout + xử lý edge-to-edge window insets |
| `app/src/main/res/drawable` | Icon vector và bản đồ vector tĩnh, không dùng ảnh mạng |

## Mở trên Android Studio (Windows)

1. Giải nén ZIP project hoặc clone repository GitHub sau khi tạo.
2. Mở Android Studio → **Open** → chọn thư mục project `ParkPin`.
3. Chọn **Gradle JDK = 17** (Settings → Build, Execution, Deployment → Build Tools → Gradle).
4. Nếu Android Studio cảnh báo thiếu SDK 37, mở SDK Manager và cài **Android API 37**.
5. Sync Gradle rồi chạy **app** trên emulator/máy thật Android 7.0 trở lên.
6. Nếu IDE không tự tạo được Gradle wrapper từ `gradle-wrapper.properties`, hãy làm theo mục **Wrapper** ở dưới.

### Xem 2 màn chưa kết nối điều hướng

- Project → `app/src/main/res/layout/screen_save_parking.xml` → **Design / Split**.
- Project → `app/src/main/res/layout/screen_history.xml` → **Design / Split**.
- Chọn một thiết bị preview (ví dụ Pixel 7) và theme `Theme.ParkPin`.
- Muốn xem **trên emulator** mà chưa gắn điều hướng: tạm đổi `<include layout="@layout/screen_home"...>` trong `activity_main.xml` thành `@layout/screen_save_parking` hoặc `@layout/screen_history`, chạy lại, sau đó trả về `screen_home`.

### Chú ý về Gradle wrapper

Bản ZIP tạo trong môi trường giới hạn mạng **không bao gồm file binary `gradle-wrapper.jar`**.
Có `gradle/wrapper/gradle-wrapper.properties` trỏ đến Gradle 9.6.0, nhưng nếu Sync báo lỗi thiếu `GradleWrapperMain`:

- Cách 1 (dễ nhất): Trong Android Studio, tạo project **Empty Views Activity** mới (`Java`) dùng phiên bản AGP hiện có. Sao chép thư mục `app/src/main/` từ starter này sang project mới, đổi namespace/applicationId thành `com.tranquochuy.parkpin`, và thêm dependencies trong `app/build.gradle` từ starter.
- Cách 2: Nếu máy có Gradle 9.6+ trong PATH, chạy `gradle wrapper --gradle-version 9.6.0` ở thư mục project để tạo wrapper chính thức.

Đừng sao chép các file Gradle wrapper JAR từ nguồn không rõ tin cậy.

## Phạm vi v0.1 / bước tiếp theo

- [x] Home UI + map illustration + cards + bottom bar
- [x] UI biểu mẫu Lưu vị trí và ảnh placeholder
- [x] UI danh sách lịch sử
- [x] Bố cục edge-to-edge, responsive scroll
- [ ] Điều hướng giữa màn hình (chưa gắn theo yêu cầu)
- [ ] Quyền vị trí, GPS và lấy tọa độ thực
- [ ] Room lưu vị trí xe
- [ ] Google Maps Intent tìm đường
- [ ] Camera / Photo Picker và lưu ảnh

Không có API key, Google Services hay yêu cầu INTERNET trong bản UI này.

## Bản vá tương thích AGP 9.4.0 (2026-11-09)

Phiên bản trước dùng AGP 9.5.0 khiến Android Studio hỗ trợ tối đa AGP 9.4.0 từ chối sync.
Đã thay duy nhất plugin Gradle gốc sang `9.4.0`; Gradle wrapper tiếp tục khai báo `9.6.0`.
Các file UI Java/XML không thay đổi, không thêm xử lý nút bấm hay nghiệp vụ.

Để sửa một project đã mở mà không cần tải lại ZIP, vào `build.gradle` ở thư mục gốc và dùng:

```groovy
plugins {
    id 'com.android.application' version '9.4.0' apply false
}
```

Sau đó chạy **File → Sync Project with Gradle Files**.
Lưu ý: ZIP vẫn chưa chứa binary `gradle-wrapper.jar` như đã mô tả ở mục Wrapper ở trên; đây là giới hạn độc lập với lỗi AGP.

Tài liệu: https://developer.android.com/build/releases/agp-9-4-0-release-notes

## Kế hoạch phát triển và trạng thái

Xem [docs/ROADMAP.md](docs/ROADMAP.md) để theo dõi 14 ngày triển khai, mốc version và checklist nghiệm thu.
Baseline `v0.1.1-ui` là **UI tĩnh**; Home đã được chạy thành công trên Emulator theo ảnh người dùng cung cấp. Không suy diễn các chức năng GPS, Room, điều hướng màn hình đã hoạt động.
