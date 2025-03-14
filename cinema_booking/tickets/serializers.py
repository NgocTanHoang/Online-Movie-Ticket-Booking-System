from rest_framework import serializers
from .models import User, Movie, Theater, Room, Showtime, Ticket, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'address', 'role']

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class TheaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theater
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    theater = TheaterSerializer()

    class Meta:
        model = Room
        fields = '__all__'

class ShowtimeSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()
    room = RoomSerializer()

    class Meta:
        model = Showtime
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    showtime = ShowtimeSerializer()

    class Meta:
        model = Ticket
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    ticket = TicketSerializer()

    class Meta:
        model = Transaction
        fields = '__all__'