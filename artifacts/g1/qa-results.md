# G1 QA — 23/11/2026 (Asia/Bangkok)

Báo cáo đầy đủ, môi trường, bảng 9 ca và ảnh: [G1_ACCEPTANCE.md](../../docs/G1_ACCEPTANCE.md).

HEAD đầu vào `74c1f880c60b60fdc1ce334a24244c309afa1d98` cùng bản sửa insets trong commit chứa báo cáo. Source `app/` Git tree: `459f8c9c93c1969f96768547ab9068f9dbd5400d`. JDK 17.0.21.1; Gradle 9.6.0; SDK 37.0. AVD Medium_Phone, emulator 37.2.12.0, Android 17 / API 37, image 37.2 PlayStore 16 KB x86_64.

APK build và APK kéo lại từ Emulator cùng SHA-256 `1ce25483e6c6e8cdb0d405f889475f567514dec63b2eec12da9bf45a1b71897d`.

| Gate | Status | Evidence |
|---|---|---|
| G0 Preflight | PASS | `preflight.json`, `jdk17.txt`, `gradle-version.txt` |
| G1 Build | PASS | `build.log`: BUILD SUCCESSFUL in 32s; `apk-verification.json` |
| G2 Emulator QA | 9/9 PASS | `test-results.json`, `acceptance-run.txt`, `emulator.log` |
| G3 Visual QA | PASS | Đã mở đủ `screenshots/G1-01-home.png` tới `G1-05-rotation.png`, ảnh toast và History cuối landscape |
| G4 Crash & Regression | PASS | `crash-analysis.json`, `logcat-app.log`, keyboard regression red/green |
| G5 Documentation | PASS | Báo cáo nghiệm thu, Roadmap, README và bằng chứng |
| G6 PR Readiness | Theo CI HEAD mới trên PR | Chỉ chuyển Ready for Review sau khi CI commit nghiệm thu SUCCESS; không merge |

| Test | Status | Evidence |
|---|---|---|
| T01 Launch | PASS | `G1-01-home.xml/png`, `T01-fragments.txt` |
| T02 Bottom Navigation | PASS | `G1-02-save.xml`, `G1-03-history.xml`, `T02-home.xml` |
| T03 Home Save CTA | PASS | `T03-home-save-cta.xml`, `T03-fragments.txt` |
| T04 History shortcut / 3 điểm mẫu | PASS | `T04-history-shortcut.xml`, `T04-fragments.txt` |
| T05 Find Car | PASS | Toast G3 thực tế đã mở ảnh kiểm tra; `T05-foreground.txt` vẫn ParkPin, không mở Maps |
| T06 Cuộn 3 màn | PASS | `T06-home-bottom.xml`, `T06-save-bottom.xml`, `T06-history-landscape-bottom.xml` |
| T07 Keyboard | PASS | Nhập `QA-G1`; IME mở, cuộn cuối form; `T07-keyboard-input.xml`, `T07-ime.txt`, `G1-04-keyboard.png` |
| T08 Rotation | PASS | `G1-05-rotation.xml/png`, `T08-fragments.txt`, `T08-history-restored-portrait.xml` |
| T09 Back | PASS | `T09-history-back-home.xml`, `T09-save-back-home.xml`, `T09-home-exit.xml` |

Đã sửa 1 lỗi insets làm thanh tab phình lên 1.094 px khi mở IME. Sau sửa thanh tab giữ 211 px; form cuộn tới cuối. Không đổi XML/dữ liệu demo, không thêm G2/G3. Lỗi nghiêm trọng còn mở: **0**. Logcat UID ParkPin: 414 dòng, 0 crash marker; crash buffer không tham chiếu ParkPin. Không tính lỗi hệ thống không liên quan.

CI HEAD đầu vào SUCCESS: [run #4](https://github.com/Hunny-17/ParkPin/actions/runs/42659897946). Final HEAD và CI run mới được ghi trên [PR #1](https://github.com/Hunny-17/ParkPin/pull/1) sau push. Local QA **PASS**; **G1 FULL PASS / READY TO MERGE** chỉ công bố sau xác minh CI HEAD mới.

Chạy lại sau khi cài APK, khởi động Emulator và đặt `ANDROID_HOME` (tùy chọn `ANDROID_SERIAL`):

```powershell
python artifacts/g1/run-acceptance.py
python artifacts/g1/check-keyboard.py artifacts/g1/G1-02-save.xml artifacts/g1/G1-04-keyboard.xml
```

Script dùng thiết bị thật, ghi ảnh và hierarchy. Phải mở ảnh toast/Visual QA riêng; script không suy diễn PASS từ source và không tự cập nhật PR.
