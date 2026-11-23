# ParkPin G4 — Photo Picker + ảnh vị trí đỗ xe

Ngày thực thi và nghiệm thu: **23/11/2026**, Asia/Bangkok.
Branch: `codex/g4-photo-picker`. G4 đã hiện thực và nghiệm thu local; PR G4 được
push/mở sau commit, chỉ Ready khi CI HEAD cuối SUCCESS. Không tự merge G4.

## PR #3 và main

Theo yêu cầu mới của người dùng, PR #3 đã merge tại
`44aac930382d87bec3f8bd6c08aa83bdc25fc2f2`. Đã xác minh **CI push trên chính main
SHA này SUCCESS**: [run 45159706681](https://github.com/Hunny-17/ParkPin/actions/runs/45159706681).
[Snapshot Actions API](../artifacts/g4/main-ci.json). G4 bắt đầu từ main đã merge.

## Hành vi G4 đã triển khai

- Một ảnh tùy chọn cho mỗi vị trí. Photo Picker ImageOnly; preview, đổi và bỏ ảnh.
- Thay/bỏ ảnh là bản nháp cho đến khi nhấn Lưu. Cancel hoặc Back giữ dữ liệu cũ.
- Ảnh được sao chép vào private files dưới dạng JPEG, cạnh dài tối đa 1600 px;
  nguồn tối đa 20 MB. Nhập/giải mã ngoài main thread; áp dụng EXIF orientation.
- Room v3 thêm photoPath nullable, migration v1→v2→v3 không xóa bản ghi/GPS.
- Home/History hiển thị ảnh; ảnh lỗi/mất có thông báo và vẫn lưu thủ công được.
- ViewModel/SavedStateHandle giữ ảnh nháp khi xoay/nhận kết quả picker. Save bị
  khóa khi import hoặc đang lưu, tránh dữ liệu ảnh dở dang/nhấn trùng.
- Thay/bỏ/xóa record chỉ dọn ảnh cũ sau khi DB thành công và không còn tham chiếu.
  Dọn ảnh nháp bị bỏ; ảnh nháp bỏ lại do process chết được prune sau 24 giờ.
- History chỉ tải bitmap của ảnh trong viewport; rời viewport/destroy thì giải
  phóng và hủy callback cũ. Giữ nguyên bố cục/card/màu/Bottom Navigation G1–G3.
- Không thêm quyền đọc toàn bộ media/storage/camera; không backend, upload hoặc
  camera capture. `PickVisualMedia` có document-picker fallback theo AndroidX.

[Thiết kế](G4_DESIGN.md), [kế hoạch](superpowers/plans/2026-11-23-g4-photo-picker.md),
[Photo Picker API](https://developer.android.com/training/data-storage/shared/photo-picker),
[AndroidX EXIF](https://developer.android.com/jetpack/androidx/releases/exifinterface).

## Build và tests thực tế

JDK Microsoft 17.0.21.1+2-LTS; Gradle 9.6.0, compile/target SDK 37, min SDK 24.
Medium_Phone bản sao riêng, emulator-5556, Emulator 37.2.12.0 build 16428233,
Android 17/API 37.2 Google Play x86_64 16 KB. Không dùng userdata AVD gốc.

| Kiểm tra | Kết quả |
|---|---|
| RED trước implementation | 5 tests chạy, 5 failure đúng vì chưa có storage/column/migration |
| RED cho nhận xét review bitmap | 1 test chạy, 1 failure trước API clear/cancel |
| Clean build trước đổi EXIF | PASS, 37 giây, 69 tasks |
| Build/JVM/test APK/lint sau đổi EXIF | PASS, 52 giây |
| JVM cuối | **4/4 PASS**, 0 failure/error/skip, từ XML |
| Gradle connected ở vòng implementation | **12/12 PASS** |
| Instrumentation cuối sau sửa EXIF | **16/16 PASS**, ADB `am instrument`, 1.532 giây |
| Android lint cuối | **0 errors, 108 warnings**, không còn warning dùng platform EXIF |
| APK build/cài | SHA-256 khớp: `b66cfc360df2d321db2418f24280881375c103445b86ffee28fc0c18dfc6383c` |
| Smoke APK cuối | Picker → Save → restart → Delete PASS; Room và owned files rỗng sau cleanup |

Lệnh clean build đã chạy:

```powershell
.\gradlew.bat --no-daemon :app:clean :app:assembleDebug :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

Sau cập nhật EXIF đã chạy lại assembleDebug/testDebugUnitTest/assembleDebugAndroidTest/
lintDebug, cài lại APK cuối bằng `adb install -r`, và chạy toàn bộ instrumentation:

```text
adb -s emulator-5556 shell am instrument -w -r com.tranquochuy.parkpin.test/androidx.test.runner.AndroidJUnitRunner
OK (16 tests)
```

ADB runner cuối giữ dữ liệu QA, thay vì Gradle connected tự uninstall target.
[Build](../artifacts/g4/build.log), [build cuối](../artifacts/g4/final-build.log),
[instrumentation cuối](../artifacts/g4/instrumentation-final.log),
[test names/counts](../artifacts/g4/automated-tests.json),
[lint](../artifacts/g4/lint-final.txt), [smoke](../artifacts/g4/final-smoke-results.json),
[APK verification](../artifacts/g4/final-verification.json).

## Nâng cấp APK G3 → G4: PASS

Dùng APK G3 đã nghiệm thu từ main, UI tạo hai record: A có GPS thật từ provider,
B thủ công. Đọc Room v2; force-stop và `install -r` G4, không clear/uninstall data.
Room v3 giữ nguyên mọi field cũ của cả hai record (ID, nội dung, active, timestamps,
lat/lng/accuracy/capturedAt); photoPath mới NULL. PhotoStorage/EXIF không thay đổi
schema migration sau ca này. Migration 1→3 và 2→3 cũng chạy trong suite cuối.

[Before/after đầy đủ](../artifacts/g4/migration-results.json),
[log](../artifacts/g4/migration.log). Không sửa SQL trên DB app trong các ca UI;
DB/WAL chỉ được sao chép để đọc. SQL fixture chỉ thuộc instrumentation test DB riêng.

## Photo Picker, ảnh, GPS và Maps UI: 16/16 PASS

| ID | Kết quả | Quan sát thực tế |
|---|---|---|
| P01 | PASS | Actual system Photo Picker opened with only selected-media access; cancelled via Back without adding a photo |
| P02 | PASS | Selected photo preview survived portrait/landscape with identical owned draft file; Room unchanged until Save |
| P03 | PASS | Saved private JPEG and Room photoPath; GPS retained; force-stop/new process retained identical rows and photo |
| P04 | PASS | Deleted only source QA fixture A from shared media; private saved JPEG and Home photo remained after restart |
| P05 | PASS | Manual edit kept photo/GPS; update succeeded with software keyboard visible and button entirely above navigation |
| P06 | PASS | Back after choosing a replacement discarded only the new draft; original photo and Room row unchanged |
| P07 | PASS | Explicit replacement saved a new owned JPEG and deleted old unreferenced file after DB success; GPS preserved |
| P08 | PASS | Removing a photo then leaving without Save kept the committed photo and file |
| P09 | PASS | Photo-only new C saved without GPS; History images loaded at top/bottom and again when scrolling back after viewport cleanup |
| P10 | PASS | Confirmed deletion removed photo record C and only its owned file; A photo retained |
| P11 | PASS | Explicit remove plus Save cleared nullable photoPath and removed owned file; parking/GPS retained |
| P12 | PASS | Simulated missing owned QA photo: friendly error, no crash; manual update still succeeded without silently clearing path/GPS |
| P13 | PASS | Rotated while system picker was open; selected photo returned to correct edit; explicit GPS recapture saved photo and new provider fix to same ID |
| P14 | PASS | G3 regression: active parking with photo launched real Maps using exact Room destination; Back returned to ParkPin |
| P15 | PASS | Manual-only B activation preserved single-active invariant; Find Car stayed in ParkPin with no-GPS toast |
| P16 | PASS | Deleted only UI-created QA A/B/C; Room and owned photo directory both empty; no data clearing |

Ảnh thử nghiệm được tạo rõ nhãn **PARKPIN QA A/B**, không sử dụng ảnh cá nhân.
P11 Home rỗng vì record active C đã bị xóa; A/B còn trong History, được đối chiếu
bằng Room. P12 cố ý xóa file ảnh QA để kiểm tra fallback; sau đó xử lý bằng UI.
P14 kiểm tra activity/Intent Maps và Back, không tuyên bố đã tính được tuyến đường.
Android 17 picker có nút Done; cold-start Maps có dialog quyền riêng. Runner chờ
đúng các trạng thái này trước khi ghi PASS; các lần runner lỗi ban đầu còn trong log.

[Kết quả từng case](../artifacts/g4/photo-results.json),
[UI execution log](../artifacts/g4/photo-ui.log),
[Intent Maps](../artifacts/g4/maps-activity.txt).

## Hồi quy CRUD/navigation: 10/10 + 6/6 PASS

| ID | Kết quả | Quan sát thực tế |
|---|---|---|
| T01 | PASS | Empty Room database; Home and History show actual empty states |
| T02 | PASS | Blank and whitespace-only names blocked; validation visible; database remains empty |
| T03 | PASS | Saved A through form; exact Home details and all database fields verified |
| T04 | PASS | B is the only active record; A remains archived |
| T05 | PASS | History shows A and B, with B active and A archived |
| T06 | PASS | Edited B in place; ID retained; exact name/floor/zone/column/note updated in Home and Room |
| T07 | PASS | A reactivated; edited B inactive; exactly one active record |
| T08 | PASS | Force-stop killed process; new process reopened; both rows and active A persisted unchanged |
| T09 | PASS | Cancel preserved both records; confirmed deletion removed only B from History and Room |
| T10 | PASS | Deleted only QA-created A; Home and History returned to empty; zero database rows |
| R01 | PASS | Five consecutive save taps produced exactly one B row; total A+B=2 |
| R02 | PASS | Software keyboard open; Update button fully above Bottom Navigation; update succeeded with IME open |
| R03 | PASS | Edit form and Save tab survive portrait/landscape rotation without crash or lost values |
| R04 | PASS | 18 rapid tab transitions completed; Home valid; database unchanged; crash checks reviewed separately |
| R05 | PASS | Home CTA/History shortcut/Find Car empty-state toast; 3-screen scrolling; History rotation; Back from both tabs and Home exit passed |
| R06 | PASS | Required-name error clears after entering a valid name |

[CRUD results](../artifacts/g4/crud-results.json),
[regression log](../artifacts/g4/regression.log). Không lặp toàn bộ 7 quyền/9 Maps
cases của acceptance G3; lần này xác minh GPS preservation/recapture, active,
Maps destination/Back và no-GPS cùng các DB/GPS tests.

## Visual QA

Đã mở từng ảnh dưới đây. Các màn ParkPin không tràn ngang, font Việt đúng,
controls cuộn tới được, nút Save/Update không bị IME/Bottom Navigation che.
Ảnh được giữ đúng sau xoay/restart và scroll History. Màn Maps là app ngoài đang
loading; bằng chứng đích chính xác nằm trong `maps-activity.txt`.

| Screenshot thực tế | Kết quả xem ảnh |
|---|---|
| [G4-01-migrated-home](../artifacts/g4/screenshots/G4-01-migrated-home.png) | PASS |
| [G4-02-system-picker](../artifacts/g4/screenshots/G4-02-system-picker.png) | PASS |
| [G4-03-picker-cancelled](../artifacts/g4/screenshots/G4-03-picker-cancelled.png) | PASS |
| [G4-04-selected-preview](../artifacts/g4/screenshots/G4-04-selected-preview.png) | PASS |
| [G4-05-draft-landscape](../artifacts/g4/screenshots/G4-05-draft-landscape.png) | PASS |
| [G4-06-home-photo](../artifacts/g4/screenshots/G4-06-home-photo.png) | PASS |
| [G4-07-history-photo](../artifacts/g4/screenshots/G4-07-history-photo.png) | PASS |
| [G4-08-home-after-restart](../artifacts/g4/screenshots/G4-08-home-after-restart.png) | PASS |
| [G4-09-keyboard](../artifacts/g4/screenshots/G4-09-keyboard.png) | PASS |
| [G4-10-replaced-photo](../artifacts/g4/screenshots/G4-10-replaced-photo.png) | PASS |
| [G4-11-photo-removed](../artifacts/g4/screenshots/G4-11-photo-removed.png) | PASS |
| [G4-12-image-unavailable](../artifacts/g4/screenshots/G4-12-image-unavailable.png) | PASS |
| [G4-13-history-top](../artifacts/g4/screenshots/G4-13-history-top.png) | PASS |
| [G4-14-history-scrolled](../artifacts/g4/screenshots/G4-14-history-scrolled.png) | PASS |
| [G4-15-delete-photo-dialog](../artifacts/g4/screenshots/G4-15-delete-photo-dialog.png) | PASS |
| [G4-16-photo-and-gps](../artifacts/g4/screenshots/G4-16-photo-and-gps.png) | PASS |
| [G4-17-maps-regression](../artifacts/g4/screenshots/G4-17-maps-regression.png) | EXTERNAL_MAPS_HANDOFF_OBSERVED |
| [G4-18-final-empty](../artifacts/g4/screenshots/G4-18-final-empty.png) | PASS |

[Manifest/hash ảnh](../artifacts/g4/visual-review.json),
[smoke preview APK cuối](../artifacts/g4/screenshots/final-smoke-preview.png),
[smoke restart APK cuối](../artifacts/g4/screenshots/final-smoke-restarted.png).

## Review, lỗi đã sửa và crash QA

- Review độc lập phát hiện bitmap History bị giữ cho mọi row; đã thêm viewport
  loading, clear/cancel và test RED→GREEN. Review lại không còn lỗi material;
  đã thực sự cuộn xuống/lên để kiểm tra ảnh nạp lại.
- Lint phát hiện platform EXIF trên Android cũ; đổi sang AndroidX EXIF 1.4.2,
  build/lint và 16 tests chạy lại PASS. Warning EXIF đã hết.
- Không có crash nghiêm trọng ParkPin trong các luồng đã chạy và log được thu.
  Lỗi UWB service của emulator được tách khỏi ParkPin. Assertion từ RED tests
  chủ động không được coi là crash ứng dụng production.

[Review](../artifacts/g4/review.md), [crash trước đổi EXIF](../artifacts/g4/crash-analysis.json),
[crash/log sau đổi EXIF](../artifacts/g4/crash-analysis-final.json),
[logcat trước](../artifacts/g4/logcat-app.log), [logcat cuối](../artifacts/g4/logcat-final.log).
Logcat là buffer volatile; phạm vi từng lần thu được ghi rõ, không khẳng định giữ
toàn bộ log qua lần restart AVD.

## Bảo toàn môi trường và giới hạn

Bảy file cấu hình/userdata/encryption/SD của AVD gốc giữ nguyên hash/kích thước/
timestamp: [verification](../artifacts/g4/original-avd-verification.json).
Chỉ dùng bản sao AVD trong workspace. Không `pm clear`. Các record QA được xóa
qua dialog UI; fixture shared media, test package, quyền và settings được dọn/
khôi phục; QA emulator dừng sau chạy cuối.

[Restore](../artifacts/g4/environment-restored-final.json).

Không còn lỗi material mở. Giới hạn: kiểm thử runtime trên API 37.2, chưa chạy
API 24/thiết bị thật/document-picker fallback/cloud provider; không stress hàng
trăm record qua UI. Các guards API24, giới hạn ảnh, EXIF, cleanup và hủy decode
được review/test/lint; không gọi đó là kiểm thử runtime API24. Lint còn 108 warning
không chặn build. Ảnh được chuẩn hóa JPEG, không giữ nguyên file gốc/animation.

## Commit và PR

Commit chứa báo cáo này là commit G4 tổng hợp. Xác định SHA bằng
`git log -1 --format=%H -- docs/G4_ACCEPTANCE.md`. Final HEAD, PR URL và CI được
công bố trong handoff/PR sau push; tránh tự tham chiếu hash của chính báo cáo.
G4 được review qua PR, không tự merge vào main.
