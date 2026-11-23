# ParkPin G2 — Final Emulator Acceptance

## Kết quả và source

Nghiệm thu thực tế ngày **23/11/2026 (Asia/Bangkok)**: **10/10 CRUD PASS**, **6/6 kiểm tra bổ sung/hồi quy PASS**, **1/1 JVM test PASS**, **5/5 instrumentation tests PASS**. Visual QA và Crash QA **PASS** trên cấu hình bên dưới.

- Repository: `Hunny-17/ParkPin`; branch `feat/g2-room-parking-crud`; [PR #2](https://github.com/Hunny-17/ParkPin/pull/2).
- HEAD đầu vào đã xác minh: `d65de9fec2c8bbb878df5c360237ea090e9d4ff6`.
- Source được kiểm thử: HEAD trên cùng bản sửa validation trong commit chứa báo cáo. Git tree toàn bộ `app/`: `4fd2251eaf624eb6893aaf5e6b4336068e670275`.
- Blob `SaveParkingFragment.java` cuối: `3c13f7f62e8753cfa1d343d0556a9a5e84cfbbc2`. Phạm vi sửa ứng dụng: 10 dòng thêm để xóa thông báo required-name khi người dùng nhập tên hợp lệ. Không đổi XML, Room schema hoặc chức năng G3.
- SHA commit chứa báo cáo: `git log -1 --format=%H -- docs/G2_ACCEPTANCE.md`; đối chiếu source đã chạy bằng `git rev-parse HEAD:app`.
- CI đầu vào: [Android build run #9 — SUCCESS](https://github.com/Hunny-17/ParkPin/actions/runs/45129916132). Final HEAD và CI run sau push được ghi trong mô tả PR #2; không lấy CI đầu vào làm bằng chứng CI commit mới.

## G0 — Preflight và bảo toàn dữ liệu

Working tree source ban đầu sạch, checkout đúng branch/HEAD yêu cầu. Dùng **Microsoft OpenJDK 17.0.21.1+2-LTS**, **Gradle Wrapper 9.6.0**, **AGP 9.4.0**, **SDK Platform 37.0**.

AVD có sẵn **Medium_Phone**, emulator **37.2.12.0 / build 16428233**, Android **17**, API **37**, system image **37.2 Google APIs PlayStore 16 KB x86_64**; `emulator-5554`, 1080 × 2400 / 420 dpi; landscape 2400 × 1080. Khởi động headless bằng cold boot, không wipe data hoặc lưu snapshot.

Trước instrumentation/CRUD, đã kiểm tra bằng ADB: ParkPin đang là bản G1 `0.2.0-g1` của lần QA trước và **chưa có thư mục database**. Không chạy `pm clear`, không xóa database production có sẵn. DAO tests dùng database trong bộ nhớ hoặc file riêng `parkpin-instrumented-persistence.db`; Gradle dọn test installation sau connected tests nên cài lại APK debug để chạy UI QA. Những lần chạy lại chỉ diễn ra sau khi đã xác nhận database chứa dữ liệu QA đã trở về rỗng.

CRUD chỉ tạo `QA-G2-A`, `QA-G2-B`, sửa B thành `QA-G2-B-edited`, rồi xóa chính các bản ghi này bằng dialog UI. Cuối nghiệm thu: **0 bản ghi**. Thiết lập software keyboard, auto-rotation và user rotation đã được khôi phục và đối chiếu với giá trị đầu vào.

Bằng chứng: [preflight.json](../artifacts/g2/preflight.json), [Gradle/JDK](../artifacts/g2/gradle-version.txt), [thiết lập ban đầu](../artifacts/g2/emulator-settings-before.json), [đã khôi phục](../artifacts/g2/emulator-settings-restored.json).

## G1 — Build & Database Tests

Chạy lại sau bản sửa validation bằng JDK 17:

```powershell
.\gradlew.bat --no-daemon :app:clean :app:assembleDebug :app:testDebugUnitTest :app:assembleDebugAndroidTest
.\gradlew.bat --no-daemon :app:connectedDebugAndroidTest
```

| Kiểm tra | Kết quả thực tế | Bằng chứng |
|---|---|---|
| Clean build + debug APK + androidTest APK + JVM | BUILD SUCCESSFUL, 27s, 69 tasks thực thi | [build.log](../artifacts/g2/build.log) |
| JVM `ParkingSpotTest` | 1 PASS, 0 FAIL, 0 ERROR, 0 SKIP | [XML](../artifacts/g2/test-results-jvm.xml) |
| Connected instrumentation trên Medium_Phone | BUILD SUCCESSFUL, 17s; 5 PASS, 0 FAIL, 0 ERROR, 0 SKIP | [instrumentation.log](../artifacts/g2/instrumentation.log), [XML](../artifacts/g2/test-results-instrumentation.xml) |

Năm DAO tests thực sự chạy: `persistsAfterDatabaseCloseAndReopen`, `savesOneActiveAndArchivesOlder`, `readUpdateAndDelete`, `reactivationIsAtomicAndIdempotent`, `emptyDatabaseAndHistoryOrder`. Chi tiết máy đọc: [database-tests.json](../artifacts/g2/database-tests.json).

Lần build đầu bị lỗi TLS khi Java tải `kotlin-reflect:2.0.10` từ Maven Central. Đã tải đúng JAR từ cùng nguồn HTTPS bằng Windows TLS, đối chiếu digest Maven `6b4bbabe20bdb258246f711da4bd87263391a292`, khôi phục dependency cache rồi build lại thành công. Không đổi version/repository của dự án. [Log lần đầu](../artifacts/g2/build-first-attempt.log). Cảnh báo deprecated Gradle API không phải lỗi biên dịch.

APK debug cuối build và APK kéo lại từ Emulator khớp SHA-256:

```text
c8ac8cef897412a95c236eb8111ffa6ccb9f5637228d483e7bbf54296c3f23a5
```

Xem [apk-verification.json](../artifacts/g2/apk-verification.json). Toàn bộ kết quả UI cuối bên dưới chạy trên APK này.

## G2 — CRUD Acceptance

Thao tác bằng ADB trên ứng dụng thật; UI Automator kiểm tra nội dung, tab, trạng thái và bounds sau thao tác. Sau khi UI ổn định, sao chép file database/WAL bằng `run-as`, đọc **bản sao trên host** để đối chiếu số dòng, ID, dữ liệu và active flag. Không dùng SQL để tạo/sửa/xóa dữ liệu ứng dụng.

| ID | Ca nghiệm thu | Status | Bằng chứng / quan sát |
|---|---|---|---|
| T01 | Database rỗng → Home/History Empty State | PASS | `G2-01-home-empty.xml`, `G2-02-history-empty.xml`, `database-empty.json`: 0 dòng. |
| T02 | Không nhập tên → không được lưu | PASS | Cả chuỗi rỗng và chỉ khoảng trắng đều bị chặn; có thông báo required-name; `database-invalid-name.json`, `database-whitespace-name.json`: 0 dòng. |
| T03 | Lưu A → Home chính xác | PASS | `QA-G2-A`, B2 / A / 12 / `Near_elevator_A`; Home và `database-saved-A.json` khớp. |
| T04 | Lưu B → chỉ B active | PASS | `database-saved-B-rapid-taps.json`: 2 dòng, A inactive, B active, tổng active=1. |
| T05 | History hiển thị A và B | PASS | `G2-05-history-data.xml`: đủ hai tên, 2 vị trí; nhãn B ĐANG ĐỖ, A ĐÃ LƯU. |
| T06 | Sửa B → cập nhật chính xác | PASS | B thành `QA-G2-B-edited`, B3 / C / 22 / `Edited_near_exit`; ID giữ nguyên, tổng 2 dòng; Home và `database-edited-B.json` khớp. |
| T07 | Đặt A hiện tại → B không active | PASS | `T07-history-active-A.xml`, `database-reactivated-A.json`: A active, B inactive, tổng active=1. |
| T08 | Đóng/mở app → dữ liệu tồn tại | PASS | Force-stop làm process cũ kết thúc; PID 22097 → 25665; Home đúng A, cả hai dòng và mọi trường không đổi. `G2-09-home-restarted.xml`, `restart-process.json`, `database-after-restart.json`. |
| T09 | Xóa B → biến mất khỏi History | PASS | Hủy dialog giữ 2 dòng; xác nhận xóa chỉ bỏ B. History và `database-deleted-B.json` còn đúng A. |
| T10 | Xóa A → rỗng | PASS | Xóa bằng dialog; `T10-history-empty.xml`, `G2-10-home-final-empty.xml`, `database-final-empty.json`: 0 dòng. |

| ID | Kiểm tra bổ sung | Status | Bằng chứng / quan sát |
|---|---|---|---|
| R01 | Không lưu trùng khi nhấn liên tiếp | PASS | 5 lần nhấn Lưu liên tiếp chỉ sinh một B; tổng A+B=2. |
| R02 | Keyboard không che nút lưu/cập nhật | PASS | IME thực sự mở, nút cập nhật trọn trong viewport; cập nhật B thành công khi IME vẫn mở. Bottom Navigation giữ nguyên chiều cao. `G2-08-keyboard.xml`, `keyboard-state.txt`. |
| R03 | Xoay form chỉnh sửa | PASS | Xoay ngang/dọc giữ tab Save và giá trị B, không crash; sau đó cập nhật đúng cùng ID. `R03-edit-landscape.xml`, `R03-edit-portrait.xml`. |
| R04 | Chuyển tab liên tiếp | PASS | 18 lần chuyển Home/Save/History; app còn hoạt động, Home hợp lệ và database không đổi. `R04-tab-stress.xml`, `database-after-tab-stress.json`. |
| R05 | Hồi quy G1 | PASS | Home CTA, History shortcut, cuộn cả ba màn, History giữ tab sau xoay, Back từ hai tab phụ về Home và Home thoát; Find Car chỉ toast G3, không mở Maps. `g1-regression.log`, `R05-*.xml`. |
| R06 | Validation sau sửa tên | PASS | Trước sửa: tên hợp lệ vẫn có lỗi đỏ (regression FAIL). Sau sửa: hết lỗi ngay khi nhập tên hợp lệ; rỗng/khoảng trắng vẫn không lưu được. `name-validation-red.txt`, `name-validation-green.txt`. |

**10/10 CRUD và 6/6 bổ sung PASS; không có ca FAIL/BLOCKED ở vòng cuối.** Kết quả máy đọc: [crud-results.json](../artifacts/g2/crud-results.json); thao tác: `crud-phase1.log` tới `crud-phase5.log`, [emulator.log](../artifacts/g2/emulator.log).

## G3 — Visual QA

Đã mở và kiểm tra từng ảnh thực tế của APK cuối; **PASS**:

| Ảnh yêu cầu | Bằng chứng |
|---|---|
| Home rỗng | [G2-01-home-empty.png](../artifacts/g2/screenshots/G2-01-home-empty.png) |
| Home có vị trí đã lưu | [G2-04-home-saved.png](../artifacts/g2/screenshots/G2-04-home-saved.png) |
| Save Parking | [G2-03-save-parking.png](../artifacts/g2/screenshots/G2-03-save-parking.png) |
| History có dữ liệu | [G2-05-history-data.png](../artifacts/g2/screenshots/G2-05-history-data.png) |
| Form chỉnh sửa | [G2-06-edit-form.png](../artifacts/g2/screenshots/G2-06-edit-form.png) |
| Dialog xác nhận xóa | [G2-07-delete-confirmation.png](../artifacts/g2/screenshots/G2-07-delete-confirmation.png) |
| Form khi mở bàn phím | [G2-08-keyboard.png](../artifacts/g2/screenshots/G2-08-keyboard.png) |
| Home sau khởi động lại | [G2-09-home-restarted.png](../artifacts/g2/screenshots/G2-09-home-restarted.png) |

Cũng đã mở ảnh History rỗng, cuối History landscape và toast G3. Nội dung, nút, dialog và icon/text rõ; không tràn ngang hoặc bị system bars/Bottom Navigation/IME che phần cần thao tác. Không có màn hình trắng. Phạm vi xác minh là Emulator 1080×2400 và 2400×1080, 420 dpi nêu trên.

## Logcat, lỗi đã sửa và tồn tại

[logcat-app.log](../artifacts/g2/logcat-app.log) lọc UID ứng dụng cuối **10239**, 513 dòng. Không có `FATAL EXCEPTION`, `AndroidRuntime`, `InflateException`, `Resources$NotFoundException`. Crash buffer không có tham chiếu ParkPin; lỗi hệ thống không liên quan được loại khỏi kết luận. [crash-analysis.json](../artifacts/g2/crash-analysis.json).

Đã sửa **1 lỗi UX validation G2**: sau lần submit tên rỗng, nhập tên hợp lệ vẫn giữ thông báo đỏ. Nguyên nhân là chỉ xóa `TextInputLayout.error` ở lần submit hợp lệ tiếp theo. Thêm TextWatcher xóa lỗi khi tên không còn rỗng sau trim; giữ nguyên kiểm tra bắt buộc khi submit. Có ảnh/XML trước sửa, kiểm tra red → green và toàn bộ build/tests/CRUD chạy lại trên bản sửa cuối.

**Lỗi nghiêm trọng còn mở: 0. Lỗi G2 còn mở trong phạm vi các ca đã chạy: 0.** Không triển khai GPS, Maps, camera hoặc tính năng G3.

## G4 — Kết luận và PR

Nghiệm thu cục bộ **PASS**. Chỉ chuyển PR #2 từ Draft sang Ready for Review sau khi CI của commit chứa bản sửa/báo cáo này SUCCESS. Final HEAD và run URL được cập nhật trên PR sau push; giữ Draft nếu CI FAIL/BLOCKED. Không merge PR #2.

Để chạy lại: cài APK và chỉ dùng database QA đã xác minh rỗng. `run_crud.py` từ chối chạy T01 nếu có bản ghi, không tự xóa dữ liệu để tạo điều kiện PASS:

```powershell
python -B artifacts/g2/run_crud.py 1
python -B artifacts/g2/run_crud.py 2
python -B artifacts/g2/run_crud.py 3
python -B artifacts/g2/run_crud.py 4
python -B artifacts/g2/run_crud.py 5
python -B artifacts/g2/run_regression.py
python -B artifacts/g2/check_name_validation.py artifacts/g2/G2-03-save-parking.xml
python -B artifacts/g2/finalize_evidence.py
```

Phải mở ảnh để nghiệm thu visual/toast; script không thay thế bước kiểm tra đó và không tự chỉnh trạng thái PR.
