# U5 — UI States · Design Master V1

**APPROVED / LOCKED.** Owner chốt V1 (Okay).

Nguồn chuẩn: [ParkPin-U5-Bold-Urban-V1.html](ParkPin-U5-Bold-Urban-V1.html). Mở bản tải về hoặc bản clone bằng trình duyệt. HTML tự chứa thư viện mẫu trạng thái, không cần server, không thực thi nghiệp vụ Android.

## Phạm vi đã chốt

Chuẩn hóa thành phần trạng thái từ [U0 V1.3](../u0/README.md), [U1 V1.2](../u1/README.md), [U2 V1](../u2/README.md), [U3 V1](../u3/README.md), [U4 V1](../u4/README.md). Không thiết kế lại các màn hình đã khóa.

| Nhóm | Màu nhận diện | Số mẫu |
| --- | --- | --- |
| Loading | #2563EB | 7 |
| Empty | #F4C430 | 4 |
| Error | #E87524 + #C92A2A | 8 |
| Success | #42D65B | 4 |
| Disabled | #B1B8C0 | 3 |
| Tổng | | 26 |

Nền trắng #FFFFFF, outline #142438, màu đặc, chữ và icon rõ nét. Disabled dùng xám thép để phân biệt nút không khả dụng; không dùng opacity thấp toàn bộ giao diện. Trạng thái luôn có nhãn, nội dung hoặc biểu tượng, không chỉ dựa vào màu.

## Phạm vi tích hợp sau

U5 là thư viện component dùng chung, không tạo màn hình hay Fragment mới. Loading phải bám tác vụ thật, không thêm delay hoặc tiến độ giả; Empty không được dùng thay lỗi đọc dữ liệu. Giữ luồng Room, GPS, Photo Picker, lưu/xóa và điều hướng đã nghiệm thu; các trạng thái khóa thao tác phải đúng với nghiệp vụ. Giữ nhập thủ công khi GPS đang xử lý hoặc bị từ chối. Hỗ trợ accessibility và reduced motion. Dialog, Toast, Snackbar thuộc U6; không overlap với U5.

Preview HTML đã duyệt, chưa tích hợp Android. Commit design-only lưu HTML và ghi chú khóa thiết kế, không lưu PNG riêng. Không tạo branch, PR, tag hoặc release. Tiếp theo: U6 — Dialog & Feedback.
