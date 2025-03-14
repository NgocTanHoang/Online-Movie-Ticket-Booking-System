# Định nghĩa serializers - Chuyển đổi dữ liệu giữa model và JSON cho API
from rest_framework import serializers
from ..models import User, Movie, Theater, Room, Showtime, Ticket, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'address', 'role']

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'genre', 'duration', 'poster_url', 'trailer_url', 'release_date']

class TheaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theater
        fields = ['id', 'name', 'address', 'phone']

class RoomSerializer(serializers.ModelSerializer):
    theater = TheaterSerializer()

    class Meta:
        model = Room
        fields = ['id', 'theater', 'room_number', 'total_seats']

class ShowtimeSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()
    room = RoomSerializer()

    class Meta:
        model = Showtime
        fields = ['id', 'movie', 'room', 'start_time', 'end_time', 'price']

class TicketSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    showtime = ShowtimeSerializer()

    class Meta:
        model = Ticket
        fields = ['id', 'user', 'showtime', 'seat_number', 'price', 'status', 'purchase_date']

class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    ticket = TicketSerializer()

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'ticket', 'amount', 'payment_method', 'transaction_date', 'status']