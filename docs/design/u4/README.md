# U4 — Bottom Navigation · Design Master V1

**APPROVED / LOCKED.** Owner chốt V1 (Okay).

Nguồn chuẩn: [ParkPin-U4-Bold-Urban-V1.html](ParkPin-U4-Bold-Urban-V1.html). Tải về hoặc mở từ bản clone bằng trình duyệt. HTML tự chứa preview ba màn hình, chuyển tab và mô phỏng Back về Trang chủ.

## Quyết định đã chốt

- Concept Urban Wayfinding, Bold Urban Cartoon. Kế thừa [U0 V1.3](../u0/README.md), [U1 V1.2](../u1/README.md), [U2 V1](../u2/README.md), [U3 V1](../u3/README.md).
- Nền thanh điều hướng #142438; nền tab được chọn #42D65B; icon và chữ được chọn #142438; icon và chữ chưa chọn #FFFFFF. Không dùng xám nhạt, chữ mờ hoặc nền bán trong suốt.
- Ba tab Trang chủ / Lưu xe / Lịch sử có chiều rộng bằng nhau; rounded outline icon 24px, vùng chạm tối thiểu 56px trong preview, bo góc 10px, nhãn bold, hiệu ứng 120ms, thanh cố định phía dưới.
- Chỉ một tab active; không đổi nội dung hoặc bố cục U1–U3 đã khóa. U4 là chuẩn chung cho thanh điều hướng trước đó chỉ là mẫu tham chiếu.

## Phạm vi tích hợp sau

Giữ nguyên ID bottom_nav, nav_home, nav_save, nav_history, fragment_container và hành vi hiện tại của MainActivity. Giữ điều hướng mở form chỉnh sửa, chuyển về Home sau lưu, khôi phục tab và Back. Không thay đổi Room/GPS/Photo Picker. Dùng kích thước dp/sp phù hợp, hỗ trợ font scale và accessibility, kiểm tra system bars/insets, keyboard, xoay màn hình và Back trên API 24 và API 35; không để điều hướng che nội dung form. Không thêm thời gian chờ giả.

Preview HTML đã duyệt, chưa tích hợp Android. Commit design-only lưu HTML và ghi chú khóa thiết kế, không lưu PNG riêng. Không tạo branch, PR, tag hoặc release. Tiếp theo: U5 — UI States.
