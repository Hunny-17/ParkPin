# U6 — Dialog & Feedback · Design Master V1

**LOCKED — baseline G1–G4.** Kết thúc giai đoạn thiết kế U0–U6 theo yêu cầu chuyển lại luồng nghiệp vụ. Những chức năng mở rộng chưa được chốt và không thuộc baseline này.

Nguồn chuẩn: [ParkPin-U6-Bold-Urban-V1.html](ParkPin-U6-Bold-Urban-V1.html). HTML tự chứa preview 14 mẫu; mở bằng trình duyệt, không thực thi nghiệp vụ Android.

## Quy chuẩn

Clear Feedback × Safe Actions, Bold Urban Cartoon. Dialog xác nhận xóa: header #C92A2A, nền #FFFFFF, card tên vị trí #F4C430; Hủy / Xóa rõ ràng. Success #42D65B, Warning #F4C430, Error #E87524, outline và shadow #142438. Giữ thiết kế các màn hình U0–U5.

14 mẫu: xác nhận xóa, lưu thành công, cập nhật thành công, chưa có vị trí, chưa có GPS, không có bản đồ, không mở được picker, không mở được bản đồ từ History, vị trí không còn tồn tại, lỗi dữ liệu, quyền GPS bị từ chối, Toast hệ thống, đặt hiện tại thành công, xóa thành công.

Hai mẫu Snackbar cuối là đề xuất phản hồi sau callback thành công; không thông báo thành công trước khi dữ liệu thực sự thay đổi. Không thêm Undo vào baseline: xóa bản ghi và ảnh riêng hiện là thao tác không thể hoàn tác. Các nghiệp vụ mở rộng và các delta UI tương ứng sẽ được duyệt riêng.

## Tích hợp sau

Dialog không tự xác nhận xóa, Hủy không thay đổi dữ liệu. Phản hồi không chặn tương tác; giữ lifecycle, accessibility, insets và reduced motion. Toast, Photo Picker và dialog cấp quyền của Android tuân theo hệ điều hành; không tái tạo crash Toast API 24 đã sửa, giữ application context khi dùng Toast hệ thống. Không mở rộng nghiệp vụ G1–G4 trong commit thiết kế này.

HTML và ghi chú khóa thiết kế được lưu, không lưu PNG riêng. Chưa tích hợp hoặc kiểm thử Android U6. Không tạo branch, PR, tag hoặc release.
