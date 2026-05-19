# Release Notes v1.2 Cloud Login

## Nâng cấp chính

1. Đăng nhập thật bằng email/password cục bộ.
2. Đăng ký tài khoản mới.
3. Phân quyền player / owner / admin.
4. Admin mini quản lý tài khoản và role.
5. Luồng đặt sân Pro thêm tên khách, số điện thoại, tiền cọc, mã giao dịch.
6. Cloud Login & Sync: backup JSON và Supabase snapshot push/pull.
7. Fallback SQLite để chạy ngay local hoặc demo.
8. Secrets template và SQL Supabase đi kèm.

## Ghi chú

Bản v1.2 dùng Supabase snapshot sync để bền dữ liệu hơn. Nếu cần nhiều người cập nhật realtime cùng lúc, bản tiếp theo nên là v1.3 Full Supabase Database.
