# ParkPin — Final Release QA

**Physical Device QA PASS 18/18.** Cổng phát hành dùng kết quả Android build trên đúng commit chứa báo cáo này.

Kiểm thử Emulator ngày 24–25/11/2026 và điện thoại ngày 25/11/2026, múi giờ Asia/Bangkok. Không tạo release, không phát hành APK, không merge PR hoặc tạo branch QA.

## Mã nguồn và môi trường

- Repository: `Hunny-17/ParkPin`, branch `main`.
- HEAD đầu vào đã xác minh: `f12cf4966f3168730b0edbd7cdb2aa3d7b02d405`; working tree sạch trước QA.
- Nguồn APK chạy trên điện thoại là `53b510fbbd62738c36c96cf8bc907981bad6f0b1`. Xác định SHA chứa bằng chứng điện thoại bằng `git log -1 --format=%H -- docs/RELEASE_QA.md` và đối chiếu với `head_sha` của Android build.
- JDK Microsoft **17.0.21.1+2**, Gradle **9.6.0**, compile SDK **37**.
- Emulator **37.2.12.0**, build **16428233**; AVD mới `ParkPin_Release_API24`, serial **emulator-5558**, Android **7.0 / API 24**, Google APIs, **x86_64**, **320×640**, density 160.
- Image Google chính thức revision 27; SHA-1 archive `46d09c0723b77ddba00f2281099a2c44a88ac971` đã khớp trước giải nén.
- AVD QA, image và userdata ở `.qa-tools/release-qa/`, tách khỏi AVD cũ. Bảy file cấu hình/userdata/encryption/sdcard của `Medium_Phone` khớp hash, kích thước và timestamp với bằng chứng G4: [đối chiếu](../artifacts/release-qa/original-avd-verification.json).
- Không `pm clear`. Lifecycle cài/gỡ của instrumentation chỉ diễn ra trên AVD QA mới. Lần chạy suite lại được chuẩn bị sau khi xác minh database QA rỗng; không thao tác dữ liệu điện thoại thật hoặc AVD cũ.
- APK debug đã kiểm thử: version `0.5.0-g4-dev` / code 5; SHA-256 `D4AE11CE79810F604A0597D85E0B41CEE18780AEABCC131CAD16601E015A77A7`. Chỉ lưu hash, không đưa APK vào artifact phát hành.

## Các cổng nghiệm thu

| Gate | Status | Bằng chứng |
|---|---|---|
| Preflight | PASS | [preflight.json](../artifacts/release-qa/preflight.json), [Gradle/JVM](../artifacts/release-qa/gradle-version.txt), [Emulator](../artifacts/release-qa/emulator-version.txt) |
| Build và unit tests | PASS — 4/4 | [Build sau sửa](https://github.com/Hunny-17/ParkPin/actions/runs/45456093649), JUnit `GpsFixTest` 3 + `ParkingSpotTest` 1, 0 FAIL/skip |
| API 24 Instrumentation | PASS — 19/19 | [JUnit](../artifacts/release-qa/junit-fixed-api24.xml), [CI API 24](https://github.com/Hunny-17/ParkPin/actions/runs/45456093632); 0 FAIL/error/skip |
| DocumentsUI Photo Selection | PASS | [Download folder](../artifacts/release-qa/e2e-verified/01b-download-folder.png), XML và actual Intent dump cùng thư mục |
| Photo Preview | PASS | [Preview](../artifacts/release-qa/e2e-verified/02-picked-image-preview.png); ảnh thật, nút đổi/bỏ ảnh hiện |
| Room Photo Persistence | PASS | [Trước](../artifacts/release-qa/e2e-verified/room-before.json), [sau lưu](../artifacts/release-qa/e2e-verified/room-saved.json), [JPEG giải mã được](../artifacts/release-qa/e2e-verified/private-photo.jpg) |
| Restart & History | PASS | [Room sau restart](../artifacts/release-qa/e2e-verified/room-restarted.json), [Home](../artifacts/release-qa/e2e-verified/04-home-after-restart.png), [History](../artifacts/release-qa/e2e-verified/05-history-photo.png) |
| API 24 Visual QA | PASS | Đã mở ảnh thực tế của các trạng thái bắt buộc và hồi quy; danh sách bên dưới |
| Crash & Regression | PASS sau sửa | [11/11 kiểm tra UI](../artifacts/release-qa/regression-result.json), [Logcat sau sửa](../artifacts/release-qa/logcat-post-fix.txt) |
| Physical Device QA | **PASS 18/18** | [Nghiệm thu điện thoại Android 15 / API 35](../artifacts/release-qa/physical-device/README.md) |
| CI final HEAD | Android build trên commit bằng chứng | [Push runs trên main](https://github.com/Hunny-17/ParkPin/actions/workflows/android-ci.yml?query=branch%3Amain+event%3Apush). Xác minh `head_sha` của commit này và kết luận SUCCESS. |
| Release Decision | **READY khi CI final HEAD SUCCESS** | API 24 và điện thoại thật đã PASS. Owner phê duyệt riêng việc phát hành. |

Hai workflow Android build và API 24 đã SUCCESS trên SHA nguồn `53b510fbbd62738c36c96cf8bc907981bad6f0b1`. Commit sau nghiệm thu chỉ chứa báo cáo và bằng chứng nên workflow API 24 theo bộ lọc đường dẫn giữ kết quả của SHA nguồn. [Android build nguồn](https://github.com/Hunny-17/ParkPin/actions/runs/45456093649) · [API 24 nguồn](https://github.com/Hunny-17/ParkPin/actions/runs/45456093632)

[![Android build](https://github.com/Hunny-17/ParkPin/actions/workflows/android-ci.yml/badge.svg?branch=main&event=push)](https://github.com/Hunny-17/ParkPin/actions/workflows/android-ci.yml?query=branch%3Amain+event%3Apush)
[![Android API24](https://github.com/Hunny-17/ParkPin/actions/workflows/android-api24-compat.yml/badge.svg?branch=main&event=push)](https://github.com/Hunny-17/ParkPin/actions/workflows/android-api24-compat.yml?query=branch%3Amain+event%3Apush)

## Điều tra và sửa lỗi

### 1. Script không kích hoạt mục DocumentsUI

CI tham chiếu [45217184551](https://github.com/Hunny-17/ParkPin/actions/runs/45217184551) chạy **18/18 instrumentation PASS**, nhưng dừng khi chờ `btn_remove_photo`. Đã tải artifact, mở ảnh trước/sau thao tác và tái hiện local: vẫn là DocumentsUI, chưa quay về ParkPin.

- Actual Intent từ chính nút CHỌN ẢNH: `ACTION_OPEN_DOCUMENT`, MIME `image/*`; `resultTo` là ParkPin MainActivity. Không khởi chạy một picker độc lập để giả kết quả của ứng dụng.
- Logcat ghi `input tap` sinh `TOOL_TYPE_UNKNOWN`. [AOSP Nougat DocumentHolder](https://android.googlesource.com/platform/frameworks/base/+/android-7.0.0_r1/packages/DocumentsUI/src/com/android/documentsui/dirlist/DocumentHolder.java) phân loại thao tác qua [Events](https://android.googlesource.com/platform/frameworks/base/+/android-7.0.0_r1/packages/DocumentsUI/src/com/android/documentsui/Events.java); chỉ mouse hoặc finger/stylus được xử lý ở nhánh tap. Đây là lỗi cách script phát sự kiện, không phải lỗi import ảnh.
- Cùng node/bounds lấy từ UI Automator, `adb -s emulator-5558 emu event mouse x y 0 1` rồi `... 0 0` mở được thư mục và chọn ảnh. Bỏ tọa độ offset `ty-72`; không tiêm URI hoặc gọi callback giả.
- Downloads provider của Android 7 không liệt kê PNG chỉ được `adb push`; đã mở Downloads và ghi nhận `No items`, sau đó bật Show internal storage, mở bộ nhớ trong → **Download** và chọn đúng file QA. Đây là lựa chọn file thật qua UI, không sửa database của provider.
- Long press → OPEN cũng được thao tác và xác minh trả ảnh. Script xác nhận OPEN nếu DocumentsUI còn ở trạng thái cần xác nhận; đường chạm hardware trên tên file trả trực tiếp về app.
- Preview + file JPEG riêng mới được tạo trước khi lưu, cùng MainActivity trở lại foreground, là bằng chứng kết quả được xử lý qua callback thật. Không thêm log/callback giả vào production.
- Script hiện từ chối serial không phải Emulator và database không rỗng. Runner này chỉ dành cho AVD QA, giao diện hệ thống tiếng Anh.

Bằng chứng ban đầu: [XML thất bại CI](../artifacts/release-qa/ci-failed-window.xml), [Activity routing local](../artifacts/release-qa/baseline-activities.txt), [Logcat trước sửa](../artifacts/release-qa/logcat-pre-fix.txt).

### 2. Crash Toast xác nhận lưu trên API 24

Sau khi khắc phục chọn ảnh, thao tác lưu thực tế phát hiện **ParkPin has stopped**. Đây là crash ứng dụng, không phải popup Messenger.

[Stack trace](../artifacts/release-qa/crash-save-api24.txt): `Toast.makeText` dùng Activity context → Material/AppCompat inflater tạo TextView từ layout framework → `StringBlock.get` ném `ArrayIndexOutOfBoundsException` (length 16, index 1042). Room đã ghi bản ghi trước crash.

Thêm test `findCarFeedbackDoesNotCrashOnApi24`, bấm listener Tìm xe thật để đi qua cùng đường Toast. [RED: 1 test, 1 failure](../artifacts/release-qa/toast-red-instrumentation.txt) tái hiện cùng exception. Sau đó đổi context của các Toast trong Home/Save/History sang `getApplicationContext()` để dùng inflater hệ thống. Giữ nguyên nội dung thông báo và bố cục G1–G4.

GREEN: full **19/19 instrumentation**, **4/4 JVM**, lưu/sửa/đặt hiện tại qua UI và luồng ảnh hoàn chỉnh đều PASS. Không sửa Photo Picker/Room/import production.

### 3. Vấn đề công cụ kiểm thử đã xử lý

- Đóng connection SQLite trước dọn bản sao tạm trên Windows; tránh file bị khóa.
- Một lần kiểm tra lặp đã hoàn thành chọn ảnh/lưu/restart/History/xóa nhưng UI Automator timeout 30 giây khi đọc hierarchy tiếp theo. Thêm tối đa một lần thử lại cho thao tác đọc hierarchy; tuyệt đối không tự lặp save/delete/selection. Log lỗi công cụ giữ tại `e2e-final-run.log`; lần xác minh đầy đủ sau cùng ở `e2e-verified/`.
- Không tái sử dụng WAL/SHM từ snapshot trước. Đọc DB + WAL bằng một tar capture khi UI đã ổn định, chạy `quick_check` và SELECT trên bản sao host; không ghi SQL vào app.
- Một lần Gradle báo BUILD SUCCESS dù installer từ chối package đã tồn tại. Không tính lần đó là PASS: log được giữ ở `toast-red-test.log`; test RED thực sự được chạy bằng `am instrument`, rồi full suite GREEN được chạy lại sạch trên AVD QA. Luôn kiểm tra JUnit, không chỉ exit code Gradle.

## Bảng test case thực tế

| Ca kiểm thử | Kết quả | Bằng chứng |
|---|---|---|
| Database rỗng, Home/History empty, ba tab | PASS | `screenshots/reg-home-empty.png`, `reg-history-empty.png`, XML và `regression-run.log` |
| Không nhập tên không lưu được | PASS | `screenshots/reg-name-required.png`, `database-reg-invalid.json` |
| Lưu thủ công không xin GPS | PASS | `database-reg-a.json`: latitude/longitude NULL, dữ liệu được lưu |
| Picker từ ParkPin → Download → Preview | PASS | `e2e-verified/01*.xml`, `02*.png`, `picker-activities.txt` |
| Một bản ghi QA mới, photoPath khác NULL | PASS | ID **5**, tên **QA_API24_RELEASE**, `e1665fd8-e841-4511-9c39-85425f8c1be8.jpg`; `e2e-verified/room-saved.json` |
| JPEG riêng giải mã được | PASS | Đã mở `e2e-verified/private-photo.jpg`, 120×72, đúng hai nửa xanh/navy; ảnh hiển thị trong app |
| Force-stop/reopen không xóa dữ liệu | PASS | ID/path/active giữ nguyên, bytes JPEG giống hệt; `room-restarted.json` |
| History có đúng vị trí và ảnh | PASS | `e2e-verified/05-history-photo.png` |
| Xóa qua dialog và dọn JPEG | PASS | `e2e-verified/06*`, `07*`, `room-deleted.json`, `result.json` |
| Lưu B chỉ B active; nhấn lưu liên tiếp | PASS | `database-reg-b.json`: 2 hàng A/B, duy nhất B active |
| Đổi ảnh + sửa tên, dọn ảnh cũ | PASS | `database-reg-replaced.json`, `regression-result.json` |
| Bỏ ảnh + lưu, photoPath NULL, dọn file | PASS | `database-reg-removed.json`, `screenshots/reg-photo-removed-draft.png` |
| Đặt A hiện tại, B inactive | PASS | `database-reg-reactivated.json` |
| Xóa B và A về rỗng | PASS | `database-reg-end.json`, xóa bằng UI |
| Bàn phím không che nút lưu | PASS | Đã mở IME, cuộn đến nút và bấm lưu trong lúc IME mở; `screenshots/reg-keyboard-save.png` |
| Landscape/portrait giữ tên và ảnh nháp | PASS | `screenshots/reg-landscape.png`, `reg-portrait-restored.png`, sau đó lưu được |
| Back về Home, không crash chuyển tab | PASS | `screenshots/reg-back-home.png`, 11/11 regression |
| Room CRUD, reopen, migration 1→2 và 2→3, EXIF/private files | PASS | Full JUnit 19/19, 0 skip |
| GPS và Maps trên điện thoại thật | PASS | Thiết bị cấp/từ chối quyền đúng, lưu vị trí thật và giao URI chính xác cho Google Maps. [P05–P07](../artifacts/release-qa/physical-device/README.md) |

## Ảnh thực tế đã mở kiểm tra

Các ảnh bên dưới được mở để kiểm tra nội dung ảnh, dữ liệu thật và khả năng thao tác. Các file XML cùng tên lưu selector/bounds; ảnh lỗi trước sửa được giữ riêng, không dùng làm bằng chứng PASS.

| Trạng thái | Screenshot |
|---|---|
| DocumentsUI, file trong Download | [Ảnh](../artifacts/release-qa/e2e-verified/01b-download-folder.png) |
| Preview trong form | [Ảnh](../artifacts/release-qa/e2e-verified/02-picked-image-preview.png) |
| Home sau lưu | [Ảnh](../artifacts/release-qa/e2e-verified/03-home-after-save.png) |
| Home sau restart | [Ảnh](../artifacts/release-qa/e2e-verified/04-home-after-restart.png) |
| History có ảnh | [Ảnh](../artifacts/release-qa/e2e-verified/05-history-photo.png) |
| Dialog xóa | [Ảnh](../artifacts/release-qa/e2e-verified/06-delete-confirmation.png) |
| History sau xóa | [Ảnh](../artifacts/release-qa/e2e-verified/07-after-delete.png) |
| Form khi mở bàn phím | [Ảnh](../artifacts/release-qa/screenshots/reg-keyboard-save.png) |
| Xoay ngang | [Ảnh](../artifacts/release-qa/screenshots/reg-landscape.png) |
| Trở về dọc, ảnh nháp còn | [Ảnh](../artifacts/release-qa/screenshots/reg-portrait-restored.png) |
| Bỏ ảnh khi sửa | [Ảnh](../artifacts/release-qa/screenshots/reg-photo-removed-draft.png) |

Home là màn hình cuộn; ảnh Home có ảnh được chụp ở vùng đã cuộn tới ảnh. Tên/ID/path được kiểm tra độc lập qua UI và Room, không suy đoán từ phần ngoài viewport.

## Logcat, thiết bị thật và giới hạn phát hành

Logcat trước sửa giữ nguyên crash ParkPin; cửa sổ log sau sửa được bắt đầu mới sau full suite GREEN, trước các luồng UI. Bằng chứng cuối ở `artifacts/release-qa/logcat-post-fix.txt`, `crash-post-fix.txt` và `post-fix-summary.json`; không dùng lỗi cũ để đếm crash của bản sửa. Không quan sát popup crash hệ thống khác trong các ảnh PASS đã mở.

Thiết bị `ee8318b9` giải quyết cổng thiếu điện thoại trước đây. Đã cài APK debug từ SHA nguồn sau khi xác nhận ParkPin chưa cài, kiểm tra 18 ca thực tế và dọn dữ liệu QA bằng giao diện. [Báo cáo và bằng chứng điện thoại](../artifacts/release-qa/physical-device/README.md)

Không có lỗi cản nghiệm thu. Điểm hiển thị viền nút trong History được ghi trong báo cáo điện thoại. Quyết định READY phụ thuộc kết quả Android build của đúng SHA cuối. Công bố release, tag và APK cần Owner phê duyệt.
