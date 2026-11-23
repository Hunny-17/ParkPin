# ParkPin G1 — Nghiệm thu ngày 23/11/2026

## Source và môi trường

- Ngày kiểm thử: **23/11/2026**, múi giờ **Asia/Bangkok**.
- Branch: `feat/g1-navigation-fragments-wrapper`; [PR #1](https://github.com/Hunny-17/ParkPin/pull/1).
- HEAD đầu vào: `74c1f880c60b60fdc1ce334a24244c309afa1d98`.
- Bản kiểm thử: HEAD trên cùng bản sửa insets trong commit chứa báo cáo. Git tree toàn bộ `app/`: `459f8c9c93c1969f96768547ab9068f9dbd5400d`; blob `MainActivity.java`: `1cff6f81233ad6ca37fb9256d24ef0f3d4a5d338`.
- Thư mục ban đầu chỉ có Git repository rỗng, không có source/thay đổi người dùng. Đã fetch và checkout branch G1 có sẵn, không tạo feature branch khác.
- Windows 11; Microsoft OpenJDK **17.0.21.1+2-LTS**; Gradle Wrapper **9.6.0**; AGP **9.4.0**; SDK Platform **37.0**.
- AVD **Medium_Phone**, emulator **37.2.12.0 / build 16428233**, Android **17**, API **37**, system image **37.2 Google APIs PlayStore 16 KB**, ABI **x86_64**.
- `emulator-5554`, 1080 × 2400 / 420 dpi; landscape 2400 × 1080.
- Khởi động headless, cold boot khắc phục ADB unauthorized từ snapshot. Không wipe data/ghi snapshot; đã khôi phục thiết lập bàn phím và xoay ban đầu.

## G1 — Build

**PASS.** Chạy sạch bằng JDK 17:

```powershell
.\gradlew.bat --no-daemon :app:clean :app:assembleDebug :app:testDebugUnitTest
```

`BUILD SUCCESSFUL in 32s`, 37 tasks thực thi, không có lỗi biên dịch. Unit-test task là `NO-SOURCE`, không tính là có unit tests đã chạy. Có cảnh báo Gradle deprecated API cho Gradle 10.

APK `app/build/outputs/apk/debug/app-debug.apk`, package `com.tranquochuy.parkpin`, version `0.2.0-g1` / code 2. Đã cài bằng `adb install -r` và chạy lại toàn bộ 9 ca trên APK JDK 17 cuối. APK kéo lại từ Emulator và APK build cùng SHA-256:

```text
1ce25483e6c6e8cdb0d405f889475f567514dec63b2eec12da9bf45a1b71897d
```

Bằng chứng: [build.log](../artifacts/g1/build.log), [JDK](../artifacts/g1/jdk17.txt), [Gradle](../artifacts/g1/gradle-version.txt), [APK verification](../artifacts/g1/apk-verification.json).

## CI

CI HEAD đầu vào `74c1f880…`: **SUCCESS**, Android build run #4: [42659897946](https://github.com/Hunny-17/ParkPin/actions/runs/42659897946).

CI commit chứa báo cáo được xác minh sau push; final HEAD và URL run mới được ghi trong mô tả PR #1. Không suy diễn CI HEAD mới từ run đầu vào.

## G2 — Emulator Acceptance

ADB thực hiện thao tác; UI Automator kiểm tra nội dung/tab/bounds; `dumpsys activity` kiểm tra Fragment thực tế. [Script chạy lại](../artifacts/g1/run-acceptance.py) ghi ảnh và hierarchy; ảnh được mở kiểm tra riêng.

| ID | Test case | Kết quả | Bằng chứng / quan sát |
|---|---|---|---|
| T01 | Launch | PASS | Home mặc định, `HomeFragment` active, không crash. `G1-01-home.png`, `T01-fragments.txt`. |
| T02 | Bottom Navigation | PASS | Home → Save → History → Home; tab/nội dung đúng sau từng bước. `G1-02-save.xml`, `G1-03-history.xml`, `T02-home.xml`. |
| T03 | Home Save CTA | PASS | Mở đúng `SaveParkingFragment`. `T03-home-save-cta.xml`, `T03-fragments.txt`. |
| T04 | History shortcut | PASS | `HistoryFragment` có Bãi xe trung tâm, Nhà xe khu B, Bãi xe siêu thị và nhãn 3 điểm mẫu. `T04-history-shortcut.xml`. |
| T05 | Find Car | PASS | Toast “Chỉ đường sẽ có ở G3 (GPS + Maps).”; ParkPin vẫn foreground, không mở Maps. `T05-find-car-toast.png`, `T05-foreground.txt`. |
| T06 | Scrolling | PASS | Home/Save cuộn tới cuối; History cuộn thực tế trong landscape; các dòng cuối nằm trên Bottom Navigation. `T06-*-bottom.xml/png`. |
| T07 | Keyboard | PASS | Nhập `QA-G1`, IME mở, cuộn tới nút Lưu và dòng cuối. Thanh tab 211 px khi đóng/mở IME. `T07-keyboard-input.xml`, `T07-ime.txt`, `G1-04-keyboard.png`. |
| T08 | Rotation | PASS | History vẫn selected và `HistoryFragment` active sau xoay ngang; xoay dọc lại vẫn History. `G1-05-rotation.png`, `T08-fragments.txt`. |
| T09 | Back | PASS | History → Home; Save → Home; Home → launcher. `T09-history-back-home.xml`, `T09-save-back-home.xml`, `T09-home-exit.xml`. |

**9/9 PASS, 0 FAIL, 0 BLOCKED.** [test-results.json](../artifacts/g1/test-results.json), [acceptance-run.txt](../artifacts/g1/acceptance-run.txt), [emulator.log](../artifacts/g1/emulator.log).

## G3 — Visual QA

**PASS** trên Emulator nêu trên. Đã mở kiểm tra trực tiếp đủ ảnh cuối:

- [Home](../artifacts/g1/screenshots/G1-01-home.png)
- [Save](../artifacts/g1/screenshots/G1-02-save.png)
- [History](../artifacts/g1/screenshots/G1-03-history.png)
- [Keyboard / cuối form](../artifacts/g1/screenshots/G1-04-keyboard.png)
- [Rotation](../artifacts/g1/screenshots/G1-05-rotation.png)
- [History cuối landscape](../artifacts/g1/screenshots/T06-history-landscape-bottom.png)
- [Toast G3](../artifacts/g1/screenshots/T05-find-car-toast.png)

System bars không che nội dung cần thao tác; thanh tab hiển thị đủ, giữ đúng lựa chọn; không tràn ngang, màn hình trắng hoặc icon/text mất hiển thị. Các XML, màu và dữ liệu demo giữ nguyên. Thay đổi hình học thanh tab chỉ loại bỏ padding insets bị cộng lặp.

## G4 — Crash, regression và lỗi đã sửa

**PASS.** Logcat UID ứng dụng **10233** có 414 dòng, không có `FATAL EXCEPTION`, `AndroidRuntime`, `InflateException` hoặc `Resources$NotFoundException`. Crash buffer không có tham chiếu ParkPin; không tính lỗi hệ thống không liên quan. [Logcat](../artifacts/g1/logcat-app.log), [phân tích](../artifacts/g1/crash-analysis.json).

Đã phát hiện/sửa **1 lỗi bố cục G1**: root áp dụng system bars/IME insets nhưng tiếp tục truyền xuống BottomNavigationView, làm thanh tab phình từ 274 lên 1.094 px khi mở IME; vùng form chỉ còn 360 px. Root hiện trả `WindowInsetsCompat.CONSUMED` sau khi áp dụng padding, tránh cộng lặp. Không đổi layout hoặc thêm chức năng.

Kiểm tra bounds đã FAIL trước sửa ([red](../artifacts/g1/keyboard-regression-red.txt)), PASS sau sửa ([green](../artifacts/g1/keyboard-regression-green.txt)); thanh tab cuối luôn 211 px, viewport form khi IME mở 1.243 px. [Script kiểm tra](../artifacts/g1/check-keyboard.py).

Home giữ nội dung gốc; Bottom Navigation không mất khi đổi màn; 3 địa điểm demo không đổi. **Lỗi nghiêm trọng còn mở: 0; lỗi G1 còn mở trong các ca đã chạy: 0.** GPS, Room, lưu dữ liệu, Maps, camera vẫn ngoài G1.

## G5/G6 — Kết luận và xuất bản

Build, Emulator và Visual/Crash QA cục bộ: **PASS**. README, Roadmap và bằng chứng đã cập nhật. Phạm vi sửa ứng dụng chỉ là insets G1.

**G1 FULL PASS / READY TO MERGE** chỉ công bố khi CI commit nghiệm thu mới SUCCESS và PR được chuyển Ready for Review. Trạng thái xuất bản cuối được ghi trên PR sau push; giữ Draft nếu CI FAIL/BLOCKED. Không tự merge, không triển khai G2/G3.

SHA commit chứa báo cáo: `git log -1 --format=%H -- docs/G1_ACCEPTANCE.md`. Đối chiếu `git rev-parse HEAD:app` với tree SHA đầu báo cáo để xác nhận source ứng dụng đã kiểm thử.
