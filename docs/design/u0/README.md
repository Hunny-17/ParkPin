# U0 — Splash & Loading · Design Master V1.3

**Status: APPROVED / LOCKED** — Bold Urban Cartoon, Urban Parking Signature.

Owner chốt U0 V1.2 và yêu cầu đồng bộ màu xanh trong logo ở V1.3. Bản V1.3 là chuẩn thiết kế, thay thế các preview V1–V1.2.

## Nguồn chuẩn

Mở [ParkPin-U0-Bold-Urban-V1.3.html](ParkPin-U0-Bold-Urban-V1.3.html) trực tiếp bằng trình duyệt sau khi tải về hoặc clone repo. HTML tự chứa CSS, SVG và JavaScript, có hai trạng thái Splash/Loading và nút phát lại hiệu ứng. Không cần server hoặc tài nguyên mạng. File được lưu nguyên bản, SHA-256: `d452738e4f78f419af5807b47f311b66899a9d46ac3b72966e739eda96ac0e97`.

## Thiết kế đã khóa

| Token | HEX | Sử dụng |
|---|---|---|
| Vibrant Green | #42D65B | Nền Splash/Loading và phần ghim xanh của logo |
| Traffic Yellow | #F4C430 | Nền logo, xe, điểm nhấn |
| Deep Navy | #142438 | Outline, chữ, chi tiết hệ thống |
| Urban Blue | #2563EB | Biển P, kính xe |
| Burnt Orange | #E87524 | Điểm nhấn đô thị |
| Deep Green | #056044 | Silhouette thành phố |
| Urban Sand | #D9CBB4 | Mặt đường |

Giữ nguyên hình dáng logo, minh họa, bố cục, typography, tagline “Đỗ xe. Ghim lại. An tâm đi.” và hiệu ứng V1.2; chỉ đồng bộ sắc xanh trong logo ở V1.3. Không dùng màu nhạt bạc, opacity thấp hoặc gradient trang trí. Ưu tiên màu tươi, sáng rõ và tương phản cao, không đồng nghĩa với màu tối.

## Phạm vi triển khai sau

- Splash hệ thống dùng logo và nền thương hiệu; tương thích minSdk 24 và Android 12+.
- Branded loading chỉ hiển thị khi thực sự đang chờ tác vụ; không thêm delay giả.
- Giữ reduced motion, không chặn thao tác khi không cần, không giả lập tiến độ.
- Không thay đổi Navigation, Room, GPS, Photo Picker hay dữ liệu đã nghiệm thu.
- Kiểm tra ảnh thực tế trên Emulator API 24 và điện thoại Android 15/API 35 sau tích hợp.

Đây là **design-only**; chưa tích hợp vào Android XML/Java và chưa có nghiệm thu runtime Android U0. Baseline nghiệp vụ: `be97cc2610e1cee75cf54c340f30613e75b3cea4`. Không tạo branch hay release. Không sửa U0 đã khóa nếu chưa có yêu cầu Owner. Tiếp theo: U1 — Trang chủ, kế thừa màu thương hiệu #42D65B.

Hai PNG preview của phiên duyệt có thể tái tạo từ HTML ở trên; commit này lưu nguồn HTML chuẩn và ghi chú khóa thiết kế, không lưu PNG.
