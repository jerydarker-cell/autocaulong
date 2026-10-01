# App Đặt Sân Cầu Lông — GitHub Pages + Firebase

Bản chuyển đổi từ Google Apps Script sang kiến trúc:

- **GitHub Pages**: giao diện web/PWA trong thư mục `docs/`
- **Firebase Authentication**: đăng nhập Admin bằng email + mật khẩu
- **Cloud Functions for Firebase (2nd gen)**: toàn bộ API đặt sân và quản trị
- **Cloud Firestore**: database
- **Firestore transaction**: chống hai người giữ cùng một khung giờ
- **Firestore Security Rules**: chặn trình duyệt đọc/ghi database trực tiếp
- **PWA**: có manifest + service worker, có thể thêm ra màn hình chính điện thoại

## Tính năng đã có

- Xem sân trống theo ngày và khung giờ
- Đặt 1–3 slot liên tiếp
- Tự tính giá
- Chống trùng lịch bằng transaction
- Sinh mã booking riêng
- Tra cứu bằng mã + số điện thoại
- Khách tự hủy khi lịch còn `Pending`
- Admin dashboard
- Trạng thái: Pending / Confirmed / Completed / Cancelled
- Thanh toán: Unpaid / Paid / Refunded
- Thống kê lịch hôm nay và doanh thu đã thu
- Thêm/sửa/bật/tắt sân
- Chỉnh giờ mở cửa, slot 30/60/90 phút, giá sân
- Chỉnh tên thương hiệu, hotline, địa chỉ, lưu ý đặt sân
- Đổi mật khẩu Admin
- Giao diện mobile-first, chạy trên iPhone/Android/PC

## 1. Tạo Firebase project

1. Vào Firebase Console và tạo project mới.
2. Mở **Build > Firestore Database** → tạo database.
3. Mở **Build > Authentication > Sign-in method** → bật **Email/Password**.
4. Trong Authentication > Users → tạo 1 tài khoản quản trị, ví dụ `admin@san.com`.
5. Vào **Project settings > Your apps > Web** → tạo Web App và lấy đoạn `firebaseConfig`.

## 2. Điền cấu hình Web App

Mở:

`docs/firebase-config.js`

Thay toàn bộ các giá trị `YOUR_...` bằng cấu hình Firebase Web App của bạn.

> Firebase Web API key được thiết kế để xuất hiện trong client. Không bao giờ đưa service-account JSON/private key lên GitHub.

## 3. Cài Firebase CLI và deploy backend

Yêu cầu Node.js 22.

```bash
npm install -g firebase-tools
firebase login
firebase use --add
cd functions
npm install
cd ..
firebase deploy --only functions,firestore
```

Khi deploy lần đầu, Firebase sẽ hỏi parameter:

`ADMIN_EMAILS`

Nhập đúng email Admin đã tạo ở Authentication, ví dụ:

`admin@san.com`

Có thể cấp nhiều Admin bằng dấu phẩy:

`admin1@san.com,admin2@san.com`

**Lưu ý:** triển khai Cloud Functions yêu cầu Firebase project có billing/Blaze plan. Bạn vẫn có quota miễn phí theo chính sách Firebase/Google Cloud, nhưng cần liên kết billing account để deploy Functions.

## 4. Đưa giao diện lên GitHub Pages

Project đã được chuẩn bị để dùng thư mục `docs/` làm nguồn GitHub Pages.

Trong repo GitHub:

1. **Settings**
2. **Pages**
3. Source: **Deploy from a branch**
4. Chọn branch chứa bản Firebase
5. Folder: **/docs**
6. **Save**

Sau khi GitHub build xong, link thường có dạng:

`https://USERNAME.github.io/REPOSITORY/`

## 5. Đăng nhập Admin

- Mở app → **Quản trị**
- Nhập email + mật khẩu Firebase Authentication
- Chỉ email có trong `ADMIN_EMAILS` mới gọi được API quản trị

Ngay cả khi người khác tự sửa JavaScript ở trình duyệt, Firestore Rules đang chặn toàn bộ truy cập Firestore trực tiếp; thao tác nhạy cảm phải đi qua Cloud Functions.

## Cấu trúc dữ liệu

- `settings/public`: thông tin hệ thống
- `courts/{courtId}`: sân
- `bookings/{bookingId}`: booking đầy đủ
- `courtDays/{date__court}`: khóa giao dịch theo từng sân/ngày, lưu các khoảng giờ đã chiếm để chống trùng kể cả khi đổi cấu hình slot
- `bookingCodes/{code}`: bảo đảm mã booking không trùng
- `bookingLookups/{sha256(code|phone)}`: tra cứu booking theo mã + SĐT

## Nâng cấp tiếp theo phù hợp

- VietQR tự sinh theo số tiền booking
- Giá giờ cao điểm / cuối tuần
- Mã giảm giá
- Thành viên và lịch sử đặt sân
- QR check-in tại sân
- Zalo/Telegram báo booking mới
- App Check + reCAPTCHA Enterprise để giảm bot/spam
- FCM push notification
- Báo cáo doanh thu ngày/tuần/tháng
- Xuất Excel/CSV
- Nhiều chi nhánh sân
