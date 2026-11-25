# U1 — Trang chủ · Design Master V1.2

**APPROVED / LOCKED.** Owner chốt V1.2 sau hai lượt chỉnh nền trắng.

Nguồn chuẩn: [ParkPin-U1-Bold-Urban-V1.2.html](ParkPin-U1-Bold-Urban-V1.2.html). Tải về hoặc mở từ bản clone bằng trình duyệt. HTML tự chứa CSS, SVG, JavaScript; các thao tác là mô phỏng thiết kế, không phải ứng dụng Android.

## Quyết định đã chốt

- Kế thừa U0 V1.3 [Splash & Loading](../u0/README.md): logo, xanh thương hiệu #42D65B, Bold Urban Cartoon.
- Nền trang, thanh trạng thái và nền preview: trắng thuần #FFFFFF, không kem/xám/cát ở vùng nền.
- Hero và CTA lưu xe: #42D65B; card vị trí hiện tại: #F4C430; Tìm xe: #2563EB; Lịch sử: #7048C6; mẹo nhỏ: #E87524.
- Outline, chữ chủ đạo và bóng đổ cứng: #142438; chữ tương phản theo nền. Không dùng màu pastel bạc, chi tiết mờ.
- Giữ bố cục, logo, minh họa đô thị, nội dung và phân lớp card của V1; V1.2 chỉ hoàn thiện nền trắng. Bản đồ minh họa phải có nhãn phân biệt với bản đồ thực.
- Bottom Navigation trong mẫu chỉ là tham chiếu tạm thời; thiết kế chính thức thuộc U4.

## Trạng thái trong preview

1. Chưa lưu vị trí.
2. Đã lưu vị trí thủ công.
3. Đã lưu GPS và ảnh (dữ liệu minh họa).
4. Đang đọc dữ liệu.
5. Lỗi đọc dữ liệu.

## Phạm vi tích hợp sau

Giữ nguyên ID view và hành vi hiện hữu trong screen_home.xml / HomeFragment.java: mở form lưu/chỉnh sửa, đọc bản ghi Room, ảnh riêng, GPS, Maps Intent và lịch sử. Không tạo dữ liệu mẫu trong ứng dụng. Loading gắn với tác vụ thật, không thêm delay giả. Không thay đổi nghiệp vụ G1–G4. Các trạng thái và thao tác trong HTML chỉ để duyệt trực quan. Kiểm tra lại trên Emulator API 24 và điện thoại thật Android 15/API 35 sau tích hợp.

Commit design-only lưu HTML và ghi chú khóa thiết kế, không lưu PNG riêng. Không tạo branch, PR, tag hoặc release. U1 không tự ý thiết kế lại sau khi chốt. Tiếp theo: U2 — Lưu vị trí.
