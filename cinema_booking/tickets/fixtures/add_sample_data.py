import os
import sys
import django
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinema_booking.cinema_booking.settings")
django.setup()



# Import models sau khi đã thiết lập Django
from tickets.models import Movie, Theater, Room, Showtime, Seat, SeatType

# API endpoint
BASE_URL = "http://127.0.0.1:8000/api"

def add_movies():
    movies_data = [
        {
            "title": "Địa Đạo: Mặt Trời Trong Bóng Tối",
            "description": "Phim điện ảnh đề tài kháng chiến \"Địa Đạo: Mặt Trời Trong Bóng Tối\" của đạo diễn Bùi Thạc Chuyên dự kiến ra rạp sớm từ 04/04/2025, hướng đến kỷ niệm 50 năm thống nhất đất nước.",
            "genre": "Lịch sử, Hành động",
            "director": "Bùi Thạc Chuyên",
            "duration": 128,
            "poster_url": "https://files.betacorp.vn/media%2fimages%2f2025%2f03%2f31%2f400x633%2D24%2D165808%2D310325%2D29.jpg",
            "trailer_url": "https://www.youtube.com/embed/ErgN3ehlbj4?rel=0&showinfo=0&autoplay=1",
            "release_date": "2025-04-04",
            "language": "Tiếng Việt",
            "actor": "Thái Hòa; Quang Tuấn; Diễm Hằng Lamoon; Anh Tú Wilson; Hồ Thu Anh; Uyển Ân"
        },
        {
            "title": "Cưới Ma Giải Hạn",
            "description": "Menn, một tên trộm cắp đang làm tay trong cho cảnh sát, đồng thời cũng là một gã trai thẳng chính hiệu. Ngày nọ, Menn vô tình nhặt được một bao lì xì đỏ bí ẩn và bị ràng buộc bởi khế ước siêu nhiên, bắt anh phải kết hôn với một hồn ma.",
            "genre": "Hài hước",
            "director": "Chayanop Boonprakob",
            "duration": 128,
            "poster_url": "https://files.betacorp.vn/media%2fimages%2f2025%2f04%2f09%2f400x633%2D25%2D142655%2D090425%2D72.jpg",
            "trailer_url": "https://www.youtube.com/embed/uxlsw0IIIeg?rel=0&showinfo=0&autoplay=1",
            "release_date": "2025-04-11",
            "language": "Tiếng Việt",
            "actor": "Putthipong Assaratanakul, Krit Amnuaydechkorn, Arachaporn Pokinpakorn"
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/movies/bulk_create/",
        json=movies_data,
        headers={"Content-Type": "application/json"}
    )
    print("Adding movies:", response.status_code)
    return response.json()

def add_theaters():
    theaters_data = [
        {
            "name": "CGV Vincom Center",
            "address": "72 Lê Thánh Tôn, Bến Nghé, Quận 1, TP.HCM",
            "phone": "028 3822 3333"
        },
        {
            "name": "CGV Crescent Mall",
            "address": "101 Tôn Dật Tiên, Tân Phú, Quận 7, TP.HCM",
            "phone": "028 5413 3333"
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/theaters/bulk_create/",
        json=theaters_data,
        headers={"Content-Type": "application/json"}
    )
    print("Adding theaters:", response.status_code)
    return response.json()

def add_seat_types():
    seat_types_data = [
        {
            "name": "Standard",
            "price_multiplier": 1.0,
            "description": "Ghế thường"
        },
        {
            "name": "VIP",
            "price_multiplier": 1.5,
            "description": "Ghế VIP"
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/seat-types/bulk_create/",
        json=seat_types_data,
        headers={"Content-Type": "application/json"}
    )
    print("Adding seat types:", response.status_code)
    return response.json()

def add_rooms():
    rooms_data = [
        {
            "room_number": "A1",
            "total_seats": 100,
            "rows": 10,
            "columns": 10,
            "theater": 1
        },
        {
            "room_number": "A2",
            "total_seats": 90,
            "rows": 9,
            "columns": 10,
            "theater": 1
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/rooms/bulk_create/",
        json=rooms_data,
        headers={"Content-Type": "application/json"}
    )
    print("Adding rooms:", response.status_code)
    return response.json()

def add_seats():
    seats_data = []
    for room_id in range(1, 3):
        for row in range(1, 11):
            for col in range(1, 11):
                seat_type = 1 if row <= 7 else 2  # Standard for rows 1-7, VIP for rows 8-10
                seats_data.append({
                    "row": row,
                    "column": col,
                    "active": True,
                    "room": room_id,
                    "seat_type": seat_type
                })
    
    response = requests.post(
        f"{BASE_URL}/seats/bulk_create/",
        json=seats_data,
        headers={"Content-Type": "application/json"}
    )
    print("Adding seats:", response.status_code)
    return response.json()

def add_showtimes():
    showtimes_data = []
    current_date = datetime.now()
    
    for movie_id in range(1, 3):
        for room_id in range(1, 3):
            for day in range(7):  # 7 ngày
                for time in ["10:00", "13:00", "16:00", "19:00", "22:00"]:
                    show_date = current_date + timedelta(days=day)
                    showtimes_data.append({
                        "movie": movie_id,
                        "room": room_id,
                        "show_date": show_date.strftime("%Y-%m-%d"),
                        "start_time": time,
                        "end_time": (datetime.strptime(time, "%H:%M") + timedelta(hours=2)).strftime("%H:%M"),
                        "price": 100000,
                        "reserved_seats": []
                    })
    
    response = requests.post(
        f"{BASE_URL}/showtimes/bulk_create/",
        json=showtimes_data,
        headers={"Content-Type": "application/json"}
    )
    print("Adding showtimes:", response.status_code)
    return response.json()

def main():
    print("Starting to add sample data...")
    
    # Thêm dữ liệu theo thứ tự phụ thuộc
    add_movies()
    add_theaters()
    add_seat_types()
    add_rooms()
    add_seats()
    add_showtimes()
    
    print("Sample data added successfully!")

if __name__ == "__main__":
    main() 