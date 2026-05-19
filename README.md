# Badminton Vinh Production Ready v1.1

Bản nâng cấp nhỏ tập trung vào dùng thật:

- Manage app theo vai trò: Người dùng / Chủ sân / Admin.
- Dữ liệu sân thật TP Vinh: thêm, sửa, import CSV, checklist dữ liệu.
- Luồng đặt sân vẫn đơn giản và có kiểm tra trùng giờ.
- Quản lý trạng thái đặt lịch và cọc/thanh toán demo.
- AI Ops v1.1 gọn hơn: kế hoạch hôm nay, task tự động, marketing, risk guard, chat offline.
- Cloud Production Plan: hướng dẫn chuyển sang Supabase khi public thật.
- Public Launch Checklist: kiểm tra trước khi chia sẻ link.
- Backup/Restore JSON, Health Check, SQLite local chạy ngay.

## Chạy local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy Streamlit Cloud

Upload toàn bộ file trong thư mục này lên GitHub sao cho `app.py` nằm ngoài cùng repo, sau đó Streamlit Cloud chọn `app.py`.

## Lưu ý production

SQLite phù hợp demo/local. Nếu public cho nhiều người dùng thật, nên chuyển dữ liệu chính sang Supabase hoặc database cloud.
