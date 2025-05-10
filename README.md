# Online Movie Ticket Booking System

Hệ thống đặt vé xem phim trực tuyến được xây dựng bằng Django, cho phép người dùng đặt vé, chọn ghế và thanh toán trực tuyến.

## Tính năng chính

- Quản lý phim và lịch chiếu
- Đặt vé và chọn ghế
- Thanh toán trực tuyến
- Tạo mã QR cho vé
- Quản lý khuyến mãi
- Banner quảng cáo
- FAQ
- API cho frontend
- Xử lý task bất đồng bộ

## Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL
- Redis (cho Celery)

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/your-username/Online-Movie-Ticket-Booking-System.git
cd Online-Movie-Ticket-Booking-System
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Cài đặt các dependency:
```bash
cd cinema_booking
pip install -r requirements.txt
```

4. Cấu hình database:
- Tạo database PostgreSQL
- Cập nhật thông tin database trong `cinema_booking/settings.py`

5. Chạy migrations:
```bash
python manage.py migrate
```

6. Tạo superuser:
```bash
python manage.py createsuperuser
```

7. Chạy server:
```bash
python manage.py runserver
```

8. Chạy Celery worker (trong terminal mới):
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
│   ├── static/             # Static files (CSS, JS, images)
│   ├── templates/          # HTML templates
│   ├── templatetags/       # Custom template tags
│   ├── admin.py           # Django admin configuration
│   ├── apps.py            # App configuration
│   ├── models.py          # Database models
│   ├── serializers.py     # API serializers
│   ├── tasks.py           # Celery tasks
│   ├── urls.py            # URL routing
│   └── views.py           # View logic
├── media/                  # User-uploaded files
├── manage.py              # Django management script
└── requirements.txt       # Project dependencies
```

## Models

1. **Movie**: Thông tin phim (tiêu đề, mô tả, thể loại, đạo diễn, thời lượng)
2. **Theater**: Thông tin rạp chiếu phim (tên, địa chỉ, số điện thoại)
3. **Room**: Phòng chiếu trong rạp
4. **Seat**: Ghế trong phòng chiếu
5. **Showtime**: Lịch chiếu phim
6. **Ticket**: Vé xem phim
7. **Transaction**: Giao dịch thanh toán
8. **Promotion**: Mã khuyến mãi
9. **Banner**: Banner quảng cáo
10. **FAQ**: Câu hỏi thường gặp

## API Endpoints

- `/api/movies/`: Quản lý phim
- `/api/theaters/`: Quản lý rạp chiếu
- `/api/showtimes/`: Quản lý lịch chiếu
- `/api/tickets/`: Quản lý vé
- `/api/promotions/`: Quản lý khuyến mãi

## Công nghệ sử dụng

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Task Queue**: Celery
- **Image Processing**: Pillow
- **QR Code**: qrcode
- **API Documentation**: Swagger/OpenAPI

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request để đóng góp.

## Giấy phép

MIT License