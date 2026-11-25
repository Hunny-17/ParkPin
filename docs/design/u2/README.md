# U2 — Lưu vị trí · Design Master V1

**APPROVED / LOCKED.** Owner chốt bản V1.

Nguồn chuẩn: [ParkPin-U2-Bold-Urban-V1.html](ParkPin-U2-Bold-Urban-V1.html). Tải về hoặc mở từ bản clone bằng trình duyệt. HTML tự chứa CSS, SVG, JavaScript; dữ liệu và hành vi trong preview chỉ là mô phỏng.

## Quyết định đã chốt

- Kế thừa [U0 V1.3](../u0/README.md) và [U1 V1.2](../u1/README.md): Bold Urban Cartoon, nền trắng #FFFFFF, logo và xanh thương hiệu #42D65B.
- GPS: #2563EB; thông tin bãi đỗ: #F4C430; ảnh: #E87524; nút lưu: #42D65B; ô nhập trắng #FFFFFF; outline và typography chủ đạo #142438; lỗi #C92A2A.
- Giữ bố cục, phân nhóm có số thứ tự, card phân lớp, viền đậm, màu tươi và tương phản rõ của preview V1.
- Bottom Navigation vẫn là mẫu tham chiếu tạm thời, thiết kế chính thức thuộc U4.

## 14 trạng thái đã duyệt

| Nhóm | Trạng thái |
| --- | --- |
| Form | Trống; thiếu tên bắt buộc |
| GPS | Đang lấy; có GPS; từ chối quyền; thất bại |
| Ảnh | Đang xử lý; có ảnh; lỗi ảnh |
| Chỉnh sửa | Chỉnh sửa; đang tải bản ghi |
| Lưu | Đang lưu; thất bại; thành công |

## Phạm vi tích hợp sau

Giữ nguyên hành vi và ID view tương ứng trong screen_save_parking.xml / SaveParkingFragment.java. Chỉ tên bãi đỗ là bắt buộc. GPS và ảnh là tùy chọn; cho phép nhập và lưu thủ công theo nghiệp vụ hiện tại. Giữ Photo Picker hệ thống, quản lý ảnh riêng, Room CRUD, quyền GPS, trạng thái xử lý, validation, chống lưu lặp và điều hướng Home sau lưu thành công. Không tạo dữ liệu GPS hoặc bản ghi mẫu trong ứng dụng, không thêm thời gian chờ giả. Trạng thái loading phải phản ánh tác vụ thật; không sửa nghiệp vụ G1–G4. Kiểm thử Android API 24 và điện thoại thật API 35 sau tích hợp, gồm bàn phím, xoay màn hình, nhập liệu, lưu, GPS và ảnh.

Commit design-only lưu HTML và ghi chú khóa thiết kế; không lưu PNG riêng. Không tạo branch, PR, tag hoặc release. Không tự sửa U2 đã chốt. Tiếp theo: U3 — Lịch sử.
