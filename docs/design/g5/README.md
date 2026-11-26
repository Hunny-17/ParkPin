# G5-P1 — Parking Lifecycle · UI Delta V1

**APPROVED / LOCKED.** Owner chốt preview V1.

Nguồn chuẩn: [ParkPin-G5-P1-Lifecycle-V1.html](ParkPin-G5-P1-Lifecycle-V1.html). HTML tự chứa, mở bằng trình duyệt, dùng dữ liệu mô phỏng liên thông giữa Trang chủ, Lưu xe và Lịch sử. Kế thừa [Design Master V1.0](../README.md); không ghi đè U0–U6 đã khóa.

## Phần bổ sung đã duyệt

- U1: khối thời gian đỗ màu vàng #F4C430, số đếm giờ/phút/giây navy #142438, nhãn ĐANG ĐỖ, thời điểm bắt đầu, nút ĐÃ LẤY XE xanh #42D65B. Giữ thông tin vị trí, GPS, ảnh và thao tác cũ.
- U2: sử dụng form hiện có; xác nhận khi lưu vị trí mới trong lúc đang có phiên.
- U3: khối phiên gần nhất trong card vị trí, thời điểm bắt đầu/kết thúc, thời lượng, lý do kết thúc và số phiên đã ghi nhận. Đặt hiện tại bắt đầu phiên mới, không ghi đè phiên trước.
- U5/U6: trạng thái dữ liệu cũ không rõ thời gian, đang kết thúc, thất bại, xác nhận kết thúc/chuyển phiên, phản hồi thành công. Kết thúc phiên không phải xóa: dùng xanh, không dùng đỏ. Giữ bản ghi và ảnh sau kết thúc. Hủy không thay đổi phiên.
- U0/U4: không thay đổi.

## Giới hạn và bước tiếp theo

Preview đã được owner duyệt về UI; mô phỏng bộ đếm, kết thúc, chuyển phiên, chỉnh sửa và mở lại ứng dụng, không thực hiện giao dịch Room hoặc Android thật. Không coi kết quả preview là nghiệm thu ứng dụng. Không lưu PNG riêng.

G5-P2 cần chốt mô hình Room V4 (vị trí và phiên riêng), migration dữ liệu cũ không suy đoán thời lượng, tính nguyên tử và duy nhất của phiên hoạt động, chính sách xóa vị trí có nhiều phiên, quy tắc đồng hồ thay đổi. Chưa phê duyệt mặc định các quyết định dữ liệu chưa thống nhất. Giữ nguyên G1–G4, không thêm nhắc giờ, camera, chi phí, Undo hoặc các gói ngoài G5.

Commit này chỉ lưu thiết kế; chưa triển khai Android/Room V4, chưa tạo branch, PR, tag, release.
