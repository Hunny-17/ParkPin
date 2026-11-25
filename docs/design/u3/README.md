# U3 — Lịch sử · Design Master V1

**APPROVED / LOCKED.** Owner chốt bản V1.

Nguồn chuẩn: [ParkPin-U3-Bold-Urban-V1.html](ParkPin-U3-Bold-Urban-V1.html). Tải về hoặc mở từ bản clone bằng trình duyệt. HTML tự chứa CSS, SVG, JavaScript; dữ liệu và thao tác là mô phỏng thiết kế, không truy cập Room hoặc GPS thực.

## Quyết định đã chốt

- Kế thừa [U0 V1.3](../u0/README.md), [U1 V1.2](../u1/README.md), [U2 V1](../u2/README.md): Bold Urban Cartoon, nền trắng #FFFFFF, logo và xanh thương hiệu #42D65B, outline và typography #142438.
- Tổng số vị trí: #7048C6; header đang đỗ: #42D65B; header đã lưu: #F4C430; chỉ đường: #2563EB; thông tin ảnh: #E87524; xóa: #C92A2A.
- Giữ nguyên bố cục card hai lớp và phân nhóm tầng, khu, cột. Phân biệt trạng thái bằng cả nhãn và màu.
- Nút Đặt hiện tại chiếm toàn chiều ngang, Sửa và Xóa trên hàng riêng. Không hiển thị Đặt hiện tại cho vị trí active; chỉ hiển thị Chỉ đường khi có tọa độ. Thiết kế này xử lý nguy cơ cắt viền PP-VIS-01; chưa xác minh bản Android.
- Minh họa riêng khi lịch sử trống. Bottom Navigation và dialog trong mẫu là tham chiếu tạm thời cho U4/U6.

## Trạng thái đã duyệt

Danh sách đã lưu (active/inactive, có/không ảnh, có/không GPS); lịch sử trống; đang tải lịch sử; lỗi đọc lịch sử; đang tải ảnh; lỗi tải ảnh; tên vị trí dài. Preview cũng mô phỏng đặt hiện tại, hủy và xác nhận xóa.

## Phạm vi tích hợp sau

Giữ nguyên nghiệp vụ và ID view tương ứng của screen_history.xml, item_parking_spot.xml, HistoryFragment.java: dữ liệu Room, thứ tự danh sách, một vị trí active, sửa/xóa/đặt hiện tại, xác nhận trước xóa, Maps Intent chỉ khi có tọa độ, hiển thị ảnh riêng và vòng đời tải ảnh theo viewport. Không thêm dữ liệu giả vào ứng dụng, không thêm delay giả. Giữ khả năng đọc chữ tiếng Việt, chiều cao nút thích ứng, target chạm phù hợp, viền đầy đủ cả khi tên hoặc nhãn xuống dòng. Kiểm tra thực tế API 24 và thiết bị API 35 sau tích hợp, bao gồm PP-VIS-01, các trạng thái tải/lỗi/empty và hồi quy CRUD/ảnh/GPS.

Commit design-only lưu HTML và ghi chú khóa thiết kế; không lưu PNG riêng. Không tạo branch, PR, tag hoặc release. Không tự sửa U3 đã chốt. Tiếp theo: U4 — Bottom Navigation.
