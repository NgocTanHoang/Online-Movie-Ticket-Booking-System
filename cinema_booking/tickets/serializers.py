from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, Theater, Room, Showtime, Ticket, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class TheaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theater
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    theater = TheaterSerializer(read_only=True)

    class Meta:
        model = Room
        fields = '__all__'

class ShowtimeSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Showtime
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    showtime = ShowtimeSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    ticket = TicketSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
