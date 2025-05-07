from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User
from ..models import Movie, Theater, Room, Showtime, Ticket, Transaction, Seat, SeatType
from .serializers import (
    UserSerializer, MovieSerializer, TheaterSerializer, RoomSerializer,
    ShowtimeSerializer, TicketSerializer, TransactionSerializer, SeatSerializer, SeatTypeSerializer
)
from django.utils import timezone
import uuid
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import qrcode
import io
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.db import transaction, connection
from django.db.models import Max

# ViewSets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'date_joined']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['genre', 'language']
    search_fields = ['title', 'description', 'director', 'actor']
    ordering_fields = ['release_date', 'title']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TheaterViewSet(viewsets.ModelViewSet):
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'address']
    ordering_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SeatTypeViewSet(viewsets.ModelViewSet):
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['theater']
    search_fields = ['room_number']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShowtimeViewSet(viewsets.ModelViewSet):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['movie', 'room', 'show_date']
    search_fields = ['movie__title']
    ordering_fields = ['show_date', 'start_time']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        showtime = self.get_object()
        booked_seats = Ticket.objects.filter(
            showtime=showtime,
            status__in=['pending', 'paid']
        ).values_list('seat_number', flat=True)
        
        room = showtime.room
        # Tạo danh sách tất cả ghế dựa trên rows và columns
        all_seats = []
        for row in range(1, room.rows + 1):
            for col in range(1, room.columns + 1):
                seat_number = f"{chr(64 + row)}{col}"  # A1, A2, ..., B1, B2, ...
                all_seats.append(seat_number)
        
        available_seats = [seat for seat in all_seats if seat not in booked_seats]
        return Response({'available_seats': available_seats})

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['showtime', 'status']
    ordering_fields = ['purchase_date']

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_with_qr(self, request):
        try:
            data = request.data
            showtime_id = data.get('showtime_id')
            seats = data.get('seats', [])
            payment_method = data.get('payment_method', 'cash')

            if not showtime_id or not seats:
                return Response(
                    {'error': 'Missing required fields: showtime_id and seats'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                showtime = Showtime.objects.get(id=showtime_id)
            except Showtime.DoesNotExist:
                return Response(
                    {'error': f'Showtime with ID {showtime_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate total price based on seats and their types
            total_price = Decimal('0')
            selected_seats = []
            
            for seat_id in seats:
                try:
                    seat = Seat.objects.get(id=seat_id)
                    selected_seats.append(seat)
                    seat_price = showtime.price * Decimal(str(seat.seat_type.price_multiplier))
                    total_price += seat_price
                except Seat.DoesNotExist:
                    return Response(
                        {'error': f'Seat with ID {seat_id} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                except Exception as e:
                    return Response(
                        {'error': f'Error calculating price for seat {seat_id}: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            try:
                with transaction.atomic():
                    # Create ticket with auto-incrementing ID
                    ticket = Ticket.objects.create(
                        user=request.user,
                        showtime=showtime,
                        status='pending',
                        price=total_price
                    )

                    # Add seats to ticket immediately after creation
                    if selected_seats:
                        ticket.seats.set(selected_seats)
                        # Force a refresh to ensure seats are saved
                        ticket.refresh_from_db()

                    # Create transaction
                    transaction_obj = Transaction.objects.create(
                        user=request.user,
                        ticket=ticket,
                        amount=total_price,
                        payment_method=payment_method,
                        status='pending'
                    )

                    # Update showtime's reserved seats
                    current_reserved = showtime.reserved_seats or []
                    new_reserved = current_reserved + [seat.id for seat in selected_seats]
                    showtime.reserved_seats = list(set(new_reserved))  # Remove duplicates
                    showtime.save()

                    # Generate QR code
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr_data = {
                        'ticket_id': ticket.id,
                        'transaction_id': transaction_obj.id,
                        'showtime_id': showtime_id,
                        'seats': [seat.id for seat in selected_seats]
                    }
                    qr.add_data(json.dumps(qr_data))
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")

                    # Save QR code
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    ticket.qr_code.save(f'ticket_{ticket.id}_qr.png', ContentFile(buffer.getvalue()), save=True)

                    # Get actual saved seats for response
                    actual_seats = list(ticket.seats.values_list('id', flat=True))

                    return Response({
                        'status': 'success',
                        'ticket_id': ticket.id,
                        'transaction_id': transaction_obj.id,
                        'qr_code_url': ticket.qr_code.url if ticket.qr_code else None,
                        'seats': actual_seats,
                        'price': str(total_price)
                    }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response(
                    {'error': f'Error creating ticket or transaction: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status == 'pending':
            ticket.status = 'confirmed'
            ticket.save()
            return Response({'status': 'success'})
        return Response(
            {'error': 'Ticket is not in pending status'},
            status=status.HTTP_400_BAD_REQUEST
        )

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_method']
    ordering_fields = ['transaction_date']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def is_admin(user):
    return user.is_authenticated and user.is_staff

@api_view(['GET', 'POST'])
@user_passes_test(is_admin)
def api_showtimes(request):
    if request.method == 'GET':
        # Filter showtimes based on query parameters
        theater_id = request.GET.get('theater')
        movie_id = request.GET.get('movie')
        date = request.GET.get('date')
        status = request.GET.get('status')
        
        showtimes = Showtime.objects.select_related('room__theater', 'movie').all()
        
        if theater_id:
            showtimes = showtimes.filter(room__theater_id=theater_id)
        if movie_id:
            showtimes = showtimes.filter(movie_id=movie_id)
        if date:
            showtimes = showtimes.filter(show_date=date)
        if status:
            is_active = status == 'active'
            now = datetime.now()
            if is_active:
                showtimes = showtimes.filter(show_date__gte=now.date())
            else:
                showtimes = showtimes.filter(show_date__lt=now.date())
        
        data = [{
            'id': s.id,
            'room': {
                'id': s.room.id,
                'name': s.room.name,
                'theater': {
                    'id': s.room.theater.id,
                    'name': s.room.theater.name
                }
            },
            'movie': {
                'id': s.movie.id,
                'title': s.movie.title
            },
            'show_date': s.show_date.strftime('%Y-%m-%d'),
            'start_time': s.start_time.strftime('%H:%M'),
            'end_time': s.end_time.strftime('%H:%M'),
            'is_active': s.show_date >= now.date()
        } for s in showtimes]
        
        return Response(data)
        
    elif request.method == 'POST':
        # Create new showtime
        try:
            room_id = request.data.get('room')
            movie_id = request.data.get('movie')
            show_date = request.data.get('show_date')
            start_time = request.data.get('start_time')
            
            room = Room.objects.get(id=room_id)
            movie = Movie.objects.get(id=movie_id)
            
            # Calculate end time based on movie duration
            start_datetime = datetime.strptime(f"{show_date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=movie.duration)
            
            # Check for overlapping showtimes in the same room
            overlapping = Showtime.objects.filter(
                room=room,
                show_date=show_date,
                start_time__lt=end_datetime.time(),
                end_time__gt=start_datetime.time()
            ).exists()
            
            if overlapping:
                return Response(
                    {'error': 'Đã có lịch chiếu khác trong khoảng thời gian này'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            showtime = Showtime.objects.create(
                room=room,
                movie=movie,
                show_date=show_date,
                start_time=start_time,
                end_time=end_datetime.time()
            )
            
            return Response({'id': showtime.id}, status=status.HTTP_201_CREATED)
            
        except (Room.DoesNotExist, Movie.DoesNotExist):
            return Response(
                {'error': 'Phòng hoặc phim không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['DELETE'])
@user_passes_test(is_admin)
def api_showtime_detail(request, pk):
    try:
        showtime = Showtime.objects.get(pk=pk)
        showtime.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Showtime.DoesNotExist:
        return Response(
            {'error': 'Lịch chiếu không tồn tại'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@user_passes_test(is_admin)
def api_theater_rooms(request, theater_id):
    try:
        rooms = Room.objects.filter(theater_id=theater_id)
        data = [{'id': r.id, 'name': r.name} for r in rooms]
        return Response(data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_theaters_api(request):
    try:
        theaters = Theater.objects.all()
        theaters_data = [
            {
                'id': theater.id,
                'name': theater.name,
                'province': theater.get_province()
            }
            for theater in theaters
        ]
        return Response({'success': True, 'theaters': theaters_data})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@require_POST
@csrf_exempt
def create_ticket(request):
    try:
        data = json.loads(request.body)
        showtime_id = data.get('showtime_id')
        seats = data.get('seats', [])
        payment_method = data.get('payment_method', 'pending')
        price = data.get('price', 0)
        status = data.get('status', 'pending')
        
        if not showtime_id or not seats:
            return JsonResponse({'error': 'Missing required data'}, status=400)
            
        showtime = Showtime.objects.get(id=showtime_id)
        
        # Create new ticket without specifying ID
        ticket = Ticket.objects.create(
            showtime=showtime,
            user=request.user if request.user.is_authenticated else None,
            price=price,
            status=status
        )
        
        # Add seats to ticket
        seat_objects = []
        for seat_id in seats:
            try:
                seat = Seat.objects.get(id=seat_id)
                seat_objects.append(seat)
            except Seat.DoesNotExist:
                ticket.delete()
                return JsonResponse({'error': f'Invalid seat ID: {seat_id}'}, status=400)
        
        # Add all seats at once
        ticket.seats.add(*seat_objects)
        
        # Create transaction record with a unique transaction ID
        transaction = Transaction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            ticket=ticket,
            amount=price,
            payment_method=payment_method,
            status='pending',
            transaction_id=f"TXN-{uuid.uuid4().hex}"  # Using UUID for uniqueness
        )
        
        # Generate QR code
        qr_data = ticket.generate_qr_data()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        
        # Save QR code
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        ticket.qr_code.save(f"ticket_{ticket.id}.png", ContentFile(buffer.getvalue()), save=True)
        buffer.close()
        
        # Update showtime's reserved seats
        showtime.reserved_seats = list(set(showtime.reserved_seats + [seat.id for seat in seat_objects]))
        showtime.save()
        
        return JsonResponse({
            'success': True,
            'ticket_id': ticket.id,
            'transaction_id': transaction.transaction_id,
            'amount': price,
            'qr_code_url': ticket.qr_code.url if ticket.qr_code else None
        })
        
    except Showtime.DoesNotExist:
        return JsonResponse({'error': 'Showtime not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def update_transaction(request):
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        payment_method = data.get('payment_method')
        status = data.get('status')
        
        if not all([transaction_id, payment_method, status]):
            return JsonResponse({'error': 'Missing required data'}, status=400)
            
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        transaction.payment_method = payment_method
        transaction.status = status
        transaction.save()
        
        # Update ticket status if payment is completed
        if status == 'completed':
            ticket = transaction.ticket
            ticket.status = 'paid'
            ticket.save()
            
            # Send confirmation email (to be implemented)
            # send_ticket_confirmation(ticket)
        
        return JsonResponse({
            'success': True,
            'transaction_id': transaction.transaction_id,
            'status': transaction.status
        })
        
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)