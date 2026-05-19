# Badminton Vinh AI Cloud Sync Pro

Bản này thêm trang **☁️ Lưu trữ & đồng bộ** để dữ liệu không bị mất khi Streamlit Cloud reboot hoặc redeploy.

## Cơ chế lưu
- Local SQLite: chạy nhanh, dùng ngay.
- Backup JSON: tải về thủ công để cất giữ.
- Supabase Snapshot Sync: đẩy toàn bộ dữ liệu lên cloud và kéo về khi cần.

## Cấu hình Supabase
1. Tạo Supabase project.
2. Vào SQL Editor, chạy file `SUPABASE_SYNC_SQL.sql`.
3. Vào Streamlit Cloud → Manage app → Settings → Secrets.
4. Dán nội dung trong `STREAMLIT_SECRETS_SYNC_TEMPLATE.toml` và thay bằng thông tin thật.
5. Reboot app.
6. Vào trang `☁️ Lưu trữ & đồng bộ` → bấm đẩy snapshot lên Supabase.

## Bảo mật
Không upload `SUPABASE_SERVICE_ROLE_KEY` lên GitHub. Chỉ lưu trong Streamlit Secrets.

## Chạy local
```bash
pip install -r requirements.txt
streamlit run app.py
```
