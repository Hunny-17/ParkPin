# ParkPin G3 — Final Emulator Acceptance

Ngày nghiệm thu: **23/11/2026 (Asia/Bangkok)**. Nghiệm thu trực tiếp bằng Gradle,
ADB, UI Automator và ảnh PNG từ Android Emulator. Các cổng local bắt buộc đều PASS.
Quyết định Ready for Review được thực hiện trên PR #3 chỉ sau khi CI của commit
nghiệm thu cuối cùng SUCCESS; không merge PR.

## G0 — Preflight và bảo toàn dữ liệu

| Hạng mục | Kết quả thực tế |
|---|---|
| Branch | `feat/g3-gps-maps-intent` — dùng đúng branch hiện hữu |
| HEAD nguồn được build/test | `1574a7faf6bb26232334fe38b4df07d2ba522443` — đúng SHA yêu cầu |
| Working tree đầu vào | Sạch; không reset/ghi đè thay đổi |
| App tree đã nghiệm thu | `d40f6d6004776d4f51eace45e90100168c2ce436` |
| Commit nghiệm thu | Commit chứa báo cáo này; chỉ tài liệu, runner và bằng chứng, app tree giữ nguyên |
| JDK / Gradle / SDK | Microsoft OpenJDK 17.0.21.1+2-LTS / Gradle 9.6.0 / compile-target 37 |
| Emulator | 37.2.12.0, build 16428233; Medium_Phone, Google Play Store 16 KB x86_64, Android 17/API 37.2 |
| Thiết bị QA | `emulator-5556`, 1080×2400; bản sao profile/data AVD trong `.qa-tools/g3-avd/` |
| Play Services | 26.32.34 (260800-968093310) |
| Google Maps | 26.34.04.965633971, có cài sẵn |
| CI đầu vào | [SUCCESS — run 45137925696](https://github.com/Hunny-17/ParkPin/actions/runs/45137925696) |
| PR | [Hunny-17/ParkPin #3](https://github.com/Hunny-17/ParkPin/pull/3) |

Không dùng trực tiếp userdata AVD gốc. Không chạy `pm clear`, không sửa SQL trên DB
đang chạy. Tất cả tạo/sửa/active/xóa bản ghi nghiệm thu đều qua UI. DB/WAL chỉ được
đọc bằng `run-as` rồi truy vấn bản sao trên host. Bảy file AVD gốc (config, userdata,
encryption key và SD card/base-overlay) giữ nguyên SHA-256, kích thước và timestamp.
Maps, quyền, Location Accuracy, keyboard/rotation đã khôi phục trên bản sao QA;
fixture đã gỡ; chỉ emulator-5556 được dừng sau QA.

Bằng chứng: [preflight](../artifacts/g3/preflight.json),
[AVD trước](../artifacts/g3/original-avd-files-before.json),
[AVD sau](../artifacts/g3/original-avd-files-after.json),
[khôi phục môi trường](../artifacts/g3/environment-restored.json).

## G1 — Build và automated tests

Đã chạy đúng hai lệnh với JDK 17 và thiết bị QA riêng:

```powershell
.\gradlew.bat --no-daemon :app:clean :app:assembleDebug :app:testDebugUnitTest :app:assembleDebugAndroidTest
.\gradlew.bat --no-daemon :app:connectedDebugAndroidTest
```

| Lần chạy | Thực tế |
|---|---|
| Clean build | BUILD SUCCESSFUL, 54 giây, 69 tasks |
| JVM tests | **4 PASS, 0 FAIL, 0 ERROR, 0 SKIP** — đếm từ XML kết quả |
| Connected instrumentation | BUILD SUCCESSFUL, 16 giây; **7 PASS, 0 FAIL, 0 ERROR, 0 SKIP** |
| DAO/GPS/Migration | Cả GPS persistence và migration1To2 đều thực sự chạy trên emulator |
| APK build / cài thực tế | SHA-256 trùng nhau: `2c4884438366b8a998bf0934b6131a28a63fba83ac534685c1c89c8909d30a93` |

[Build log](../artifacts/g3/build.log), [instrumentation log](../artifacts/g3/instrumentation.log),
[tên từng test và số lượng từ XML](../artifacts/g3/automated-tests.json),
[APK verification](../artifacts/g3/apk-verification.json).

CI của PR kiểm tra assembleDebug, assembleDebugAndroidTest và testDebugUnitTest;
7 instrumentation tests trong báo cáo này là lần chạy local trên emulator.

## G2 — GPS Permission: 7/7 PASS

| ID | Kết quả | Quan sát thực tế |
|---|---|---|
| T01 | PASS | First G3 launch after real upgrade: no automatic permission dialog; request remains user initiated |
| T02 | PASS | User LẤY GPS action opened actual coarse/fine Android runtime permission dialog |
| T03 | PASS | Denied both location permissions; real manual Save succeeded with NULL coordinates |
| T04 | PASS | Coarse-only permission accepted with actual FLP fix after enabling Location Accuracy on isolated AVD: Vị trí gần đúng: 10.774775, 106.710166 (±2000 m) |
| T05 | PASS | Precise permission returned actual FLP fix: GPS: 10.776888, 106.700805 (±5 m) |
| T06 | PASS | Master location disabled: request settled with friendly manual-save message; Room unchanged and app alive |
| T07 | PASS | Enabled GPS test provider emitted no fixes: friendly timeout, manual UI update succeeded, all B GPS columns remain NULL and A unchanged |

Tọa độ được bơm bằng **Android Emulator `geo fix`**, sau đó ParkPin nhận qua Fused
Location Provider. Không gán tọa độ hardcode vào app/Room. Coarse-only được xác minh
bằng runtime permission dump (COARSE=true, FINE=false), fix thực tế sai số 2000 m;
Precise sai số 5 m. [Provider injections](../artifacts/g3/provider-injections.json),
[quyền coarse](../artifacts/g3/permissions-approximate.txt),
[provider coarse](../artifacts/g3/provider-approximate.txt),
[provider precise](../artifacts/g3/provider-precise.txt).

T07 dùng GPS test provider **enabled nhưng không phát location** trên AVD riêng,
đợi request hết hạn rồi cập nhật thủ công qua UI. Không bơm fix giả để làm ca này
PASS. Provider thử nghiệm và appops được gỡ/khôi phục sau kiểm tra.

## G3 — Room v1 → v2: PASS

Đã dùng **APK G2 thật từ app tree đã merge**
`4fd2251eaf624eb6893aaf5e6b4336068e670275`, SHA-256
`c8ac8cef897412a95c236eb8111ffa6ccb9f5637228d483e7bbf54296c3f23a5`.

1. Cài G2 trên AVD QA, xác nhận schema v1 rỗng.
2. UI tạo QA-G3-MIG-A (ID 1, inactive) và QA-G3-MIG-B (ID 2, active).
3. Đọc Room v1, force-stop, `adb install -r` APK G3, không uninstall/clear data.
4. Mở G3 và đọc Room v2. Cả hai bản ghi giữ nguyên mọi trường cũ: ID, tên,
   floor, zone, columnLabel, note, active, createdAt, updatedAt.
5. Bốn cột latitude/longitude/accuracyMeters/locationCapturedAt đều nullable và
   NULL trên dữ liệu vừa migrate; không reset database, không mất lịch sử.

[So sánh v1/v2 đầy đủ](../artifacts/g3/migration-tests.json),
[snapshot trước](../artifacts/g3/database-migration-v1-before-upgrade.json),
[snapshot sau](../artifacts/g3/database-migration-v2-after-upgrade.json),
[migration log](../artifacts/g3/migration.log). Sau đối chiếu, chỉ hai bản ghi QA
được xóa qua dialog UI để bắt đầu các ca tiếp theo.

## G4 — GPS Persistence: 8/8 PASS

| ID | Kết quả | Quan sát thực tế |
|---|---|---|
| P01 | PASS | Saved A via real form; all four GPS fields persisted and match emulator HCMC fix |
| P02 | PASS | Actual force-stop/new process retained identical rows and GPS fields |
| P03 | PASS | Manual edit updated floor/zone/column/note and preserved all four existing GPS fields |
| P04 | PASS | Explicit LẤY GPS recapture updated same A ID to real Hanoi fix and a newer capture timestamp |
| P05 | PASS | Manual-only position B saved and displayed correctly without GPS |
| P06 | PASS | Reactivated manual B from GPS A; exactly one active row, both retained |
| P07 | PASS | Confirmed UI deletion removed GPS A only; manual B retained |
| P08 | PASS | Rotated portrait/landscape during actual pending request; same B edit saved with NULL GPS, A unchanged and no crash |

A ban đầu nhận HCMC `10.7768883,106.700805`, accuracy 5 m. Lấy lại GPS chủ động
cập nhật cùng ID thành Hanoi `21.02851,105.8048167`, timestamp mới hơn. B thủ công
luôn giữ bốn trường GPS NULL. Các ảnh Home restart được chụp trước bước recapture;
ảnh form/History thể hiện dữ liệu Hanoi ở bước sau. Các snapshot Room ghi đầy đủ
giá trị và thời điểm tương ứng.

[GPS results](../artifacts/g3/gps-tests.json),
[A mới lưu](../artifacts/g3/database-gps-A-saved.json),
[A sau restart](../artifacts/g3/database-gps-A-restarted.json),
[A sau sửa thủ công](../artifacts/g3/database-gps-A-after-manual-edit.json),
[A sau recapture](../artifacts/g3/database-gps-A-recaptured.json),
[rotation pending](../artifacts/g3/gps-rotation-pending.xml).

## G5 — Maps Intent: 9/9 PASS

| ID | Kết quả | Quan sát thực tế |
|---|---|---|
| M01 | PASS | Empty Home Find Car showed friendly toast and stayed in ParkPin; zero rows |
| M02 | PASS | Saved active B has no GPS; friendly toast captured and ParkPin stayed foreground |
| M03 | PASS | Home Find Car opened installed real Google Maps activity |
| M04 | PASS | Actual Android Intent destination 21.0285100,105.8048167 equals Room A coordinates formatted to 7 decimals |
| M05 | PASS | Android Back from real Maps returned to ParkPin Home normally |
| M06 | PASS | Maps disabled only on isolated QA AVD; generic geo Intent reached separate QA-only receiver with exact Room destination. Fixture validates OS delivery, not third-party rendering. |
| M07 | PASS | No geo or Maps handler: friendly toast captured, ParkPin foreground, Room unchanged |
| M08 | PASS | Inactive GPS A History directions opened actual Maps with A Room destination |
| M09 | PASS | History manual B has no directions action; GPS A has directions |

Intent thực tế được Android ghi nhận:

```text
google.navigation:q=21.0285100,105.8048167
package=com.google.android.apps.maps
activity=com.google.android.maps.MapsActivity
```

[Intent Home](../artifacts/g3/maps-home-navigation-activity.txt),
[Intent History](../artifacts/g3/maps-history-navigation-activity.txt),
[fallback thực tế](../artifacts/g3/maps-generic-fallback-activity.txt),
[không có handler](../artifacts/g3/maps-no-handlers.txt),
[maps results](../artifacts/g3/maps-tests.json).

M06 sử dụng activity nhận `geo:` QA riêng vì AVD chỉ có Maps làm handler ban đầu.
Activity không có quyền/GPS/network, chỉ hiển thị URI Android thực sự giao đến.
Đây là kiểm chứng fallback qua OS; không tuyên bố kiểm thử giao diện hoặc tính
đường của ứng dụng bản đồ thương mại thứ hai. [Mã fixture](../artifacts/g3/fixtures/geo-handler/README.md).

## G6 — Hồi quy G1/G2: PASS

Đã chạy lại **10/10 CRUD + 6/6 regression cases**, bao phủ cả 12 nhóm yêu cầu:
ba Fragment, Back, Home CTA, form Save, CRUD, History, Edit, Delete confirmation,
active switching, keyboard insets, rotation và persistence sau restart.

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

[Kết quả CRUD](../artifacts/g3/crud-results.json),
[mapping 12 nhóm hồi quy](../artifacts/g3/regression-results.json),
[execution log](../artifacts/g3/regression.log),
[ảnh keyboard](../artifacts/g3/screenshots/REG-08-keyboard.png),
[ảnh landscape](../artifacts/g3/screenshots/R03-edit-landscape.png).

## G7 — Visual QA: 10/10 PASS

Đã **mở kiểm tra từng ảnh PNG thật**. Không tràn ngang, font tiếng Việt đúng,
ParkPin không có màn trắng/dialog lỗi; nội dung cuộn tới được, system bars và
Bottom Navigation không che controls cần thao tác. Nút cập nhật sử dụng được khi
IME mở. Trạng thái permission/GPS/Home/History khớp snapshot Room.

| Ảnh | Nội dung thực tế |
|---|---|
| [G3-01-home-no-gps](../artifacts/g3/screenshots/G3-01-home-no-gps.png) | Home bản ghi G2 vừa migrate, chưa có GPS |
| [G3-02-gps-permission](../artifacts/g3/screenshots/G3-02-gps-permission.png) | Android runtime permission do LẤY GPS mở |
| [G3-03-permission-denied](../artifacts/g3/screenshots/G3-03-permission-denied.png) | Bị từ chối quyền, vẫn lưu thủ công |
| [G3-04-approximate-location](../artifacts/g3/screenshots/G3-04-approximate-location.png) | Coarse-only fix, sai số 2000 m |
| [G3-05-precise-location](../artifacts/g3/screenshots/G3-05-precise-location.png) | Precise fix HCMC, sai số 5 m |
| [G3-06-save-with-gps](../artifacts/g3/screenshots/G3-06-save-with-gps.png) | Form A có GPS đã recapture, các trường thủ công |
| [G3-07-history-with-gps](../artifacts/g3/screenshots/G3-07-history-with-gps.png) | A có chỉ đường, B thủ công không có chỉ đường |
| [G3-08-maps-navigation](../artifacts/g3/screenshots/G3-08-maps-navigation.png) | Google Maps thật, bản đồ Hanoi và destination đã nhận |
| [G3-09-location-unavailable](../artifacts/g3/screenshots/G3-09-location-unavailable.png) | Dịch vụ vị trí tắt, thông báo phù hợp |
| [G3-10-home-after-restart](../artifacts/g3/screenshots/G3-10-home-after-restart.png) | Home A/GPS sau force-stop và mở process mới |

[Manifest ảnh/hash](../artifacts/g3/visual-review.json). Lớp bản đồ đã tải sau khi
khắc phục DNS của AVD. Google Maps báo không tính được tuyến lái xe trong phiên
giả lập; đích Intent vẫn chính xác. Không tuyên bố đã kiểm thử hành trình thực tế.

## G8 — Crash QA: PASS

Logcat theo UID ParkPin chứa 550 dòng ở lần thu cuối: không có
FATAL EXCEPTION/AndroidRuntime/SecurityException/SQLiteException/migration error/
ActivityNotFoundException; crash buffer có 0 tham chiếu ParkPin. Không có lỗi
Play Services gắn với ParkPin trong phần log được kiểm tra. No-handler và null fix
được xử lý bằng thông báo, không trở thành lỗi uncaught.

[Logcat app](../artifacts/g3/logcat-app.log),
[location services log](../artifacts/g3/logcat-location-services.log),
[crash analysis và phạm vi](../artifacts/g3/crash-analysis.json).

Logcat volatile được thu từ sau lần restart AVD để sửa DNS; log trước reboot không
được coi là còn nguyên. Các luồng migration/GPS trước đó có assertion UI/Room và
log Gradle/instrumentation, không ghi nhận process chết ngoài các force-stop chủ
động. Log hệ thống/Maps ngoài phạm vi không được dùng làm lỗi ParkPin.

## Lỗi đã sửa và giới hạn còn lại

Không phát hiện lỗi production G3 buộc phải sửa. Không thay đổi Java/XML/schema
đã được build và nghiệm thu. Đã sửa cấu hình QA (Location Accuracy, DNS) và runner
(dialog hệ thống, task Intent, nhận diện tab của Maps). Bằng chứng no-fix và các
assertion runner thất bại ban đầu được giữ lại trong execution logs.

[Chi tiết FAIL/quan sát trước và retest PASS](../artifacts/g3/qa-observations.md).

Không còn FAIL/BLOCKED chức năng ParkPin trong phạm vi bắt buộc. Giới hạn:
chạy trên một AVD Android 17/API 37.2, chưa chạy thiết bị vật lý; generic fallback
dùng QA receiver; Maps route calculation ngoài ParkPin chưa được nghiệm thu.
Không triển khai Camera, Photo Picker hoặc G4.

## G9 — Commit và PR readiness

Chỉ một commit tổng hợp tài liệu/bằng chứng sau khi local QA hoàn tất. SHA commit
cuối xác định bằng `git log -1 --format=%H -- docs/G3_ACCEPTANCE.md`; app tree phải
vẫn là `d40f6d6004776d4f51eace45e90100168c2ce436`. SHA và CI run của commit này được ghi trên
[PR #3](https://github.com/Hunny-17/ParkPin/pull/3) sau push để tránh tự tham chiếu
hash của chính file trong commit.

Điều kiện chuyển Ready: G0–G8 PASS, commit trên đúng branch hiện hữu, CI chính
HEAD mới SUCCESS. Nếu CI thất bại, giữ Draft. Không merge PR #3.
