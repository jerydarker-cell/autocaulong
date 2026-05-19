# Badminton Vinh Production Ready v1.2.1 Home Chat

Nâng cấp theo yêu cầu: thêm bảng chat online ngay tại trang chủ.

## Có gì mới
- Chat ngay trong trang chính.
- 5 phòng chat: Toàn cộng đồng, Tìm kèo, Đặt sân, Mua bán, Góp ý app.
- Tin nhắn phân biệt vai trò người chơi / chủ sân / admin.
- Admin có thể ẩn tin nhắn.
- Lưu local SQLite và hỗ trợ đồng bộ Supabase nếu cấu hình Secrets.
- Backup/Restore JSON đã bao gồm `chat_messages`.

## Lưu ý production
Muốn chat đồng bộ nhiều người bền vững trên Streamlit Cloud, hãy cấu hình Supabase và chạy SQL trong `SUPABASE_V1_2_SQL.sql`.
