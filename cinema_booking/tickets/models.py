from django.db import models
from django.contrib.auth.models import AbstractUser

# Người dùng
class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, default='registered')

# Phim
class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.CharField(max_length=50)
    duration = models.IntegerField()  # Thời lượng (phút)
    poster_url = models.URLField()
    trailer_url = models.URLField(blank=True, null=True)
    release_date = models.DateField()

    def __str__(self):
        return self.title

# Rạp chiếu phim
class Theater(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

# Phòng chiếu
class Room(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    total_seats = models.IntegerField()

    def __str__(self):
        return f"{self.theater.name} - Phòng {self.room_number}"

# Lịch chiếu
class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.movie.title} - {self.start_time}"

# Vé
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')  # pending, paid, used
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vé {self.seat_number} - {self.showtime}"

# Giao dịch (tùy chọn)
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"Giao dịch {self.id} - {self.user.username}"