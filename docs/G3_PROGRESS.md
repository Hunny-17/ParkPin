# ParkPin G3 — Emulator acceptance completed

G3 trên `feat/g3-gps-maps-intent`, dựa trên G2 đã merge tại
`87bafe7293afa455cde3fe2ed686f54bf79102ea`, đã được nghiệm thu thực tế ngày
23/11/2026. Xem [G3_ACCEPTANCE.md](G3_ACCEPTANCE.md) và [bằng chứng](../artifacts/g3/).

| Cổng local | Kết quả |
|---|---|
| Clean build / JVM / instrumentation | PASS / 4/4 / 7/7 |
| GPS permissions | 7/7 PASS |
| Room v1→v2 qua APK G2 thật | PASS, hai bản ghi giữ nguyên |
| GPS persistence | 8/8 PASS |
| Maps Intent / destination / fallback | 9/9 PASS |
| G2 CRUD / regression | 10/10 + 6/6 PASS |
| Visual / crash | 10 ảnh đã mở kiểm tra / PASS |

Không sửa production Java/XML trong lần QA. Không triển khai G4, camera, picker,
backend hoặc bản đồ nhúng. AVD gốc giữ nguyên; chỉ bản sao QA được dùng.

Generic `geo:` fallback được kiểm tra với receiver QA riêng. Google Maps nhận đúng
đích và tải lớp bản đồ, nhưng việc tính tuyến lái xe/hành trình thực tế chưa được
nghiệm thu. Phạm vi logcat theo UID và giới hạn thiết bị được nêu trong báo cáo.

[PR #3](https://github.com/Hunny-17/ParkPin/pull/3) đã Ready sau CI HEAD nghiệm thu
SUCCESS, rồi được merge theo yêu cầu tiếp theo của người dùng tại
`44aac930382d87bec3f8bd6c08aa83bdc25fc2f2`.
[CI push main SUCCESS](https://github.com/Hunny-17/ParkPin/actions/runs/45159706681).
G4 tiếp tục trên branch riêng; xem [G4_ACCEPTANCE.md](G4_ACCEPTANCE.md).
