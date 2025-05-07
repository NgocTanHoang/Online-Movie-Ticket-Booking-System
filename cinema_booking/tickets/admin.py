from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Movie, Theater, Room, SeatType, Seat, Showtime, Ticket, Transaction,
    Promotion, Banner, FAQ # Import new models
)

# Unregister the default User admin
admin.site.unregister(User)

# Register User with custom admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration', 'release_date', 'status', 'language')
    list_filter = ('status', 'genre', 'language')
    search_fields = ('title', 'director', 'actor')
    fields = ('title', 'description', 'genre', 'director', 'actor', 'duration', 'language', 'release_date', 'status', 'poster_url', 'trailer_url')

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    search_fields = ('name', 'address')

@admin.register(SeatType)
class SeatTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_multiplier')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'row', 'column', 'seat_type', 'is_active')
    list_filter = ('room', 'seat_type', 'is_active')
    search_fields = ('room__room_number',)

class SeatInline(admin.TabularInline): # Display seats within Room admin
    model = Seat
    fields = ('row', 'column', 'seat_type', 'is_active')
    readonly_fields = ('row', 'column', 'seat_type') # Make them read-only here
    extra = 0 # Don't show extra empty rows
    can_delete = False # Prevent deletion from here
    max_num = 0 # Prevent adding new seats from here

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('theater', 'room_number', 'total_seats', 'rows', 'columns')
    list_filter = ('theater',)
    search_fields = ('room_number', 'theater__name')
    # Make rows/columns read-only as they are calculated
    readonly_fields = ('rows', 'columns') 
    # Display seats as read-only inline
    inlines = [SeatInline]
    # Override form fields to control what can be edited directly
    fields = ('theater', 'room_number', 'total_seats') 

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'room', 'show_date', 'start_time', 'price')
    list_filter = ('show_date', 'movie', 'room__theater')
    search_fields = ('movie__title', 'room__room_number', 'room__theater__name')
    autocomplete_fields = ['movie', 'room'] # Easier selection for lots of movies/rooms
    readonly_fields = ('end_time', 'reserved_seats') # Make calculated/managed fields read-only
    fields = ('movie', 'room', 'show_date', 'start_time', 'price', 'end_time', 'reserved_seats')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'showtime', 'get_seats', 'status', 'purchase_date')
    list_filter = ('status', 'purchase_date', 'showtime__show_date', 'showtime__movie')
    search_fields = ('user__username', 'user__email', 'showtime__movie__title', 'id')
    autocomplete_fields = ['user', 'showtime']
    readonly_fields = ('purchase_date', 'qr_code') # QR code generated on save
    
    def get_seats(self, obj):
        return ", ".join([str(seat) for seat in obj.seats.all()])
    get_seats.short_description = 'Seats'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'ticket', 'amount', 'payment_method', 'status', 'transaction_date')
    list_filter = ('status', 'payment_method', 'transaction_date')
    search_fields = ('transaction_id', 'user__username', 'ticket__id')
    autocomplete_fields = ['user', 'ticket']
    readonly_fields = ('transaction_id', 'transaction_date')

# Register new models
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'discount_amount', 'start_date', 'end_date', 'active')
    list_filter = ('active', 'start_date', 'end_date')
    search_fields = ('code', 'description')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'link_url', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title',)
    list_editable = ('is_active', 'order') # Allow editing these directly in list view

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')
    list_editable = ('is_active', 'order')

# Note: Seat model is intentionally not registered directly
# It's managed via the Room model inline for better consistency

# You might want to customize the User admin later if needed
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User

# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     pass # Add customizations here
