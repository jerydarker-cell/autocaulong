# Badminton Vinh AI Automation Enterprise Sync

Bản nâng cấp sửa lỗi selectbox trên Streamlit Cloud và thêm AI Enterprise Automation OS.

## Sửa lỗi chính
- Sửa lỗi `TypeError` khi `st.selectbox()` nhận trực tiếp `sqlite3.Row` ở các trang Check-in, Hội viên, QR Check-in, Chủ sân Portal.
- Thêm `safe_select_row()` để render selectbox ổn định trên Streamlit Cloud.

## Nâng cấp AI
- AI Enterprise Automation OS
- AI Brain nhiều agent
- AI tự tạo task vận hành
- AI tạo chiến dịch marketing 7 ngày
- Court Ops tự động hóa
- CRM tự động
- Sync Guard
- Checklist test trước public

## Cách chạy
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Upload toàn bộ thư mục lên GitHub, đảm bảo `app.py`, `requirements.txt`, `.streamlit/` nằm ngoài cùng repo.
