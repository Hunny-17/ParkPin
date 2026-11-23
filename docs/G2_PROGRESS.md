# ParkPin G2 — Room + local CRUD integration (QA 23/11/2026)

Base: G1 merge commit `315aaf17681af2c3edca216c91b6e5a0b72c2f80`.
PR và trạng thái xuất bản cuối: https://github.com/Hunny-17/ParkPin/pull/2

## Implemented source (code review and runtime QA separate)
- Room 2.8.5 entity + DAO + database + async repository, persisted locally offline.
- One active parking entry at a time (Room transaction); older entries appear in History.
- Save Parking: manual inputs, required place name, save/update feedback, edit existing record.
- Home: displays active record or real empty state. Static map remains labeled illustrative.
- History: Room-backed records, edit, activate an older record, delete with confirmation, empty state.
- No seeded demo records, no login/Firebase, GPS, embedded Maps or camera.
- Android instrumentation DAO test source: active switching, CRUD, ordering, empty DB, persistence after close/reopen.
- Existing G1 navigation / keyboard insets retained.

## Verified on Emulator
- Clean build bằng JDK 17, Gradle 9.6 và SDK 37: PASS.
- JVM: 1/1 PASS; connected instrumentation DAO tests trên Medium_Phone API 37.2: 5/5 PASS.
- CRUD qua UI thực tế: 10/10 PASS; rapid-save, keyboard, rotation, tab stress, G1 regression và validation correction: 6/6 PASS.
- Đã mở kiểm tra đủ 8 ảnh bắt buộc; Logcat ứng dụng không có crash marker.
- Sửa 1 lỗi thông báo required-name còn đỏ sau khi nhập tên hợp lệ; kiểm tra red/green và chạy lại toàn bộ QA.
- [Báo cáo nghiệm thu](G2_ACCEPTANCE.md), bằng chứng trong `artifacts/g2/`.
- CI của final HEAD được xác minh sau push và ghi trên PR #2; chỉ chuyển Ready for Review khi SUCCESS. Không merge.

## Acceptance policy
No `allowMainThreadQueries` in production; tests may use it with an in-memory/test DB.
No destructive migration; schema changes require explicit migration in a later release.
No untested PASS claims; no merge without QA.
