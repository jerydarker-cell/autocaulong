# Badminton Vinh Production Ready v1.2.1 Cloud Login

Bản v1.2.1 tập trung vào dùng thật hơn:

- Đăng nhập email/password.
- Đăng ký tài khoản người chơi/chủ sân.
- Phân quyền giao diện: Người dùng / Chủ sân / Admin.
- Admin quản lý tài khoản và đổi role.
- Đặt sân Pro có tên, SĐT, tiền cọc, mã giao dịch.
- Backup/Restore JSON.
- Supabase Cloud Snapshot Sync tùy chọn.
- Vẫn chạy ngay bằng SQLite local.
- AI vận hành offline-first, không tốn API.

## Tài khoản demo

- player@badmintonvinh.local / player123
- owner@badmintonvinh.local / owner123
- admin@badmintonvinh.local / admin123

## Chạy local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy Streamlit Cloud

Upload toàn bộ thư mục lên GitHub. Repo cần thấy trực tiếp:

```text
app.py
requirements.txt
.streamlit/
SUPABASE_V1_2_SQL.sql
STREAMLIT_SECRETS_V1_2_TEMPLATE.toml
```

Streamlit Cloud chọn `app.py` làm main file path.

## Supabase Sync

1. Tạo Supabase project.
2. Chạy file `SUPABASE_V1_2_SQL.sql` trong SQL Editor.
3. Dán nội dung `STREAMLIT_SECRETS_V1_2_TEMPLATE.toml` vào Streamlit Secrets và thay key thật.
4. Vào app > Admin > Cloud Login & Sync để push/pull snapshot.

Không commit `SUPABASE_SERVICE_ROLE_KEY` lên GitHub.


## v1.2.2 Live Comments Board

Bản này thêm bình luận live online ngay tại trang chủ:

- Phòng chat: Toàn cộng đồng, Tìm kèo, Đặt sân, Mua bán, Góp ý app.
- Người chơi / chủ sân / admin đều chat được sau khi đăng nhập.
- Admin có thể ẩn tin nhắn không phù hợp.
- Nếu Supabase đã cấu hình và chạy SQL, chat đồng bộ cloud qua bảng `badminton_chat_messages`.
- Nếu chưa cấu hình Supabase, chat vẫn lưu local bằng SQLite để test/demo.

### SQL cần chạy thêm trong Supabase
Mở `SUPABASE_V1_2_SQL.sql` và chạy lại trong Supabase SQL Editor. File đã có thêm bảng `badminton_chat_messages`.


## v1.2.2 Live Comments
- Sửa UX: bỏ bảng chat/phòng chat.
- Thêm bình luận trực tiếp tại trang chủ kiểu phiên live.
- Bình luận mới nhất hiện trên cùng, có quick comments và admin ẩn bình luận.
