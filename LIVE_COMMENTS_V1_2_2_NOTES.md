# Badminton Vinh Production Ready v1.2.2 Live Comments

Bản này sửa theo yêu cầu: không dùng bảng chat/phòng chat nữa, mà chuyển thành **bình luận live ngay tại trang chủ** giống các phiên live.

## Thay đổi chính
- Trang chủ có mục `🔴 Live bình luận trang chủ`.
- Người dùng đăng bình luận nhanh ngay trên trang chủ.
- Bình luận mới nhất hiển thị ở trên cùng.
- Có nút bình luận nhanh: tìm kèo, hỏi sân, mua bán, góp ý app.
- Admin có thể ẩn bình luận không phù hợp.
- Vẫn lưu SQLite local và có thể đồng bộ Supabase nếu đã cấu hình.

## Lưu ý Supabase
Vẫn dùng bảng `badminton_chat_messages` để tương thích với bản cũ, nhưng UX trong app hiển thị là live comments, không còn bảng chat nhiều phòng.
