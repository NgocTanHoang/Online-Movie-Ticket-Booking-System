# Hệ thống Đặt Vé Xem Phim Trực Tuyến

Ứng dụng web xây dựng bằng Django cho phép người dùng đặt vé xem phim, chọn suất chiếu, chọn ghế và thanh toán trực tuyến. Hệ thống có giao diện quản trị hiện đại để quản lý phim, lịch chiếu, rạp, phòng chiếu, ghế, khuyến mãi, banner, FAQ...

## Tính năng chính

- Quản lý phim: thêm, sửa, xóa, chuyển trạng thái (đang chiếu, sắp chiếu, ngừng chiếu)
- Upload và hiển thị poster phim (ảnh)
- Quản lý lịch chiếu, rạp, phòng chiếu, ghế
- Đặt vé và chọn ghế trực tuyến
- Tích hợp thanh toán (có thể mở rộng)
- Sinh mã QR cho vé
- Quản lý khuyến mãi, mã giảm giá
- Quản lý banner, FAQ
- API RESTful cho frontend
- Xử lý tác vụ bất đồng bộ với Celery

## Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL
- Redis (cho Celery)
- Django 4.x+

## Hướng dẫn cài đặt

1. **Clone repository:**
   ```bash
   git clone https://github.com/your-username/Online-Movie-Ticket-Booking-System.git
   cd Online-Movie-Ticket-Booking-System
   ```

2. **Tạo và kích hoạt môi trường ảo:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Cài đặt các thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Cấu hình database:**
   - Tạo database PostgreSQL.
   - Cập nhật thông tin kết nối trong `cinema_booking/settings.py`.

5. **Chạy migrate:**
   ```bash
   python manage.py migrate
   ```

6. **Tạo tài khoản quản trị:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Chạy server phát triển:**
   ```bash
   python manage.py runserver
   ```

8. **Chạy Celery worker (ở terminal khác):**
   ```bash
   celery -A cinema_booking worker -l info
   ```

## Cấu trúc thư mục

```
cinema_booking/
├── cinema_booking/          # Cấu hình project Django
├── tickets/                 # App chính
│   ├── api/                # API endpoints
│   ├── fixtures/           # Dữ liệu mẫu
│   ├── migrations/         # Database migrations
│   ├── static/             # File tĩnh (CSS, JS, images)
│   ├── templates/          # Giao diện HTML
│   ├── templatetags/       # Custom template tags
│   ├── admin.py            # Cấu hình Django admin
│   ├── apps.py             # Cấu hình app
│   ├── models.py           # Định nghĩa models
│   ├── serializers.py      # API serializers
│   ├── tasks.py            # Celery tasks
│   ├── urls.py             # Định tuyến URL
│   └── views.py            # Xử lý logic view
├── media/                  # File upload (poster phim, v.v.)
├── manage.py               # Script quản lý Django
└── requirements.txt        # Danh sách thư viện phụ thuộc
```

## Các model chính

- **Movie (Phim):** tiêu đề, mô tả, thể loại, đạo diễn, thời lượng, poster_url (ảnh), trailer_url, ngày khởi chiếu, ngôn ngữ, diễn viên, trạng thái
- **Theater (Rạp):** tên, địa chỉ, số điện thoại, trạng thái
- **Room (Phòng chiếu):** thuộc rạp, có ghế
- **Seat (Ghế):** thuộc phòng, loại ghế
- **Showtime (Lịch chiếu):** phim, phòng, ngày, giờ, giá vé
- **Ticket (Vé):** người dùng, lịch chiếu, ghế, giá, trạng thái, mã QR
- **Transaction (Giao dịch):** thông tin thanh toán cho vé
- **Promotion (Khuyến mãi):** mã giảm giá
- **Banner:** banner trang chủ
- **FAQ:** câu hỏi thường gặp

## API Endpoints

- `/api/movies/`: Quản lý phim
- `/api/theaters/`: Quản lý rạp
- `/api/showtimes/`: Quản lý lịch chiếu
- `/api/tickets/`: Quản lý vé
- `/api/promotions/`: Quản lý khuyến mãi

## Công nghệ sử dụng

- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL
- **Task Queue:** Celery + Redis
- **Xử lý ảnh:** Pillow
- **Sinh mã QR:** qrcode
- **API Docs:** Swagger/OpenAPI
- **Frontend:** Bootstrap 5 (giao diện quản trị)

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request.

## Giấy phép

MIT License