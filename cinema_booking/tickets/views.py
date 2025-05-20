from django.views import View
from django.contrib.auth.models import User
from .models import Movie, Theater, Room, Showtime, Ticket, Transaction, Seat, SeatType, Promotion, Banner, FAQ
from .serializers import (UserSerializer, MovieSerializer, TheaterSerializer,
                         RoomSerializer, ShowtimeSerializer, TicketSerializer,
                         TransactionSerializer)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum
from collections import defaultdict
import re
import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils import timezone
import qrcode
import io
from django.core.files.base import ContentFile
from .tasks import delete_unpaid_tickets
import os
from django.conf import settings

def extract_province(address):
    # Danh sách các tỉnh thành phố đặc biệt cần xử lý
    special_cases = {
        'HCM': 'TP.HCM',
        'Hồ Chí Minh': 'TP.HCM',
        'Thành phố Hồ Chí Minh': 'TP.HCM',
        'TP Hồ Chí Minh': 'TP.HCM',
        'Ha Noi': 'Hà Nội',
        'Hanoi': 'Hà Nội',
        'HN': 'Hà Nội'
    }
    
    if not address:
        return 'Khác'
        
    # Tách địa chỉ và lấy phần cuối cùng (thường là tỉnh/thành phố)
    parts = [p.strip() for p in address.split(',')]
    province = parts[-1].strip()
    
    # Kiểm tra và chuẩn hóa tên tỉnh/thành phố
    for key, value in special_cases.items():
        if key.lower() in province.lower():
            return value
            
    return province

def auth_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'login':
            email = request.POST.get('sign-in-email')
            password = request.POST.get('sign-in-passwd')
            
            # Try to get user by email
            try:
                user = User.objects.get(email=email)
                # Authenticate with username and password
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Đăng nhập thành công!')
                    # Clear any existing theater selection from session
                    if 'selected_theater' in request.session:
                        del request.session['selected_theater']
                    return redirect('home')
                else:
                    messages.error(request, 'Mật khẩu không đúng')
            except User.DoesNotExist:
                messages.error(request, 'Email không tồn tại')
            except Exception as e:
                messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
                
        elif form_type == 'signup':
            first_name = request.POST.get('sign-up-name')
            email = request.POST.get('sign-up-email')
            password = request.POST.get('sign-up-passwd')
            password2 = request.POST.get('sign-up-passwd2')
            if not all([first_name, email, password, password2]):
                messages.error(request, 'Vui lòng điền đầy đủ thông tin')
            elif password != password2:
                messages.error(request, 'Mật khẩu xác nhận không khớp')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email đã được sử dụng')
            elif len(password) < 8:
                messages.error(request, 'Mật khẩu phải dài ít nhất 8 ký tự')
            else:
                username = email.split('@')[0]
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name
                    )
                    login(request, user)
                    messages.success(request, 'Đăng ký thành công!')
                    return redirect('home')
                except Exception as e:
                    messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
    messages_list = [
        {"message": message.message, "level": message.tags}
        for message in messages.get_messages(request)
    ]
    return render(request, 'sign_in.html', {"messages": json.dumps(messages_list)})

def logout_view(request):
    # Clear selected theater from session on logout
    if 'selected_theater' in request.session:
        del request.session['selected_theater']
        request.session.modified = True # Ensure session is saved
        
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('login') # Redirect to login after logout

def home_view(request):
    try:
        movies = Movie.objects.all()
        theaters = Theater.objects.all()
        
        # Get selected theater from session
        selected_theater = None
        if 'selected_theater' in request.session:
            try:
                selected_theater = Theater.objects.get(id=request.session['selected_theater'])
            except Theater.DoesNotExist:
                del request.session['selected_theater']
        
        # Process movie trailer URLs
        for movie in movies:
            if movie.trailer_url and "youtube.com/embed/" in movie.trailer_url:
                video_id = movie.trailer_url.split("embed/")[-1].split("?")[0]
                movie.trailer_url = f"https://www.youtube.com/embed/{video_id}"
    except Exception as e:
        movies = []
        theaters = []
        selected_theater = None
        print(f"Error loading movies: {str(e)}")
    
    return render(request, 'index.html', {
        'movies': movies,
        'theaters': theaters,
        'selected_theater': selected_theater
    })

def movies_view(request):
    movies = Movie.objects.all()
    movies_latest = Movie.objects.order_by('-release_date')
    movies_adults = Movie.objects.filter(
        Q(genre__icontains='Hoạt hình') | Q(genre__icontains='Phiêu lưu')
    ).order_by('-release_date')
    
    theaters = Theater.objects.all()
    selected_theater = None
    
    # Get selected theater info
    if 'selected_theater' in request.session:
        try:
            selected_theater = Theater.objects.get(id=request.session['selected_theater'])
        except Theater.DoesNotExist:
            del request.session['selected_theater']
    
    for movie in movies:
        if "youtube.com/embed/" in movie.trailer_url:
            video_id = movie.trailer_url.split("embed/")[-1].split("?")[0]
            movie.trailer_url = f"https://www.youtube.com/embed/{video_id}"
    return render(request, 'movies.html', {
        'movies': movies, 
        'movies_latest': movies_latest, 
        'movies_adults': movies_adults,
        'selected_theater': selected_theater,
        'theaters': theaters
    })

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if movie.trailer_url and "watch?v=" in movie.trailer_url:
        movie.trailer_url = movie.trailer_url.replace("watch?v=", "embed/")
    
    # Date selection logic
    today = datetime.now().date()
    selected_date_str = request.GET.get('date', today.isoformat())
    try:
        selected_date = datetime.fromisoformat(selected_date_str).date()
    except ValueError:
        selected_date = today

    # Generate date range for buttons
    day_range_count = 7 # Show next 7 days
    date_buttons = []
    for i in range(day_range_count):
        date_buttons.append(today + timedelta(days=i))

    # Get selected theater info
    selected_theater = None
    if 'selected_theater' in request.session:
        try:
            selected_theater = Theater.objects.get(id=request.session['selected_theater'])
        except Theater.DoesNotExist:
            del request.session['selected_theater']

    # Get showtimes for the selected date and theater
    showtimes_by_room = defaultdict(list)
    if selected_theater:
        showtimes = Showtime.objects.filter(
            movie=movie,
            room__theater=selected_theater,
            show_date=selected_date
        ).select_related('room').order_by('room__room_number', 'start_time')
        
        for showtime in showtimes:
            showtimes_by_room[showtime.room].append(showtime)

    context = {
        'movie': movie,
        'showtimes_by_room': dict(showtimes_by_room),
        'current_date': today,
        'selected_date': selected_date,
        'date_buttons': date_buttons,
        'selected_theater': selected_theater
    }
    return render(request, 'movie_detail.html', context)

def about_view(request):
    return render(request, 'about.html')

def ticket_view(request):
    return render(request, 'e-ticket.html')

def ticket_booking_view(request, movie_id, cinema):
    # Get basic objects
    movie = get_object_or_404(Movie, id=movie_id)
    theater = get_object_or_404(Theater, id=cinema)
    
    # Get today's date and selected date
    today = datetime.today().date()
    selected_date_str = request.GET.get('date', today.isoformat())
    try:
        selected_date = datetime.fromisoformat(selected_date_str).date()
    except ValueError:
        selected_date = today

    # Generate next 7 days for date selection
    days = [
        {
            'id': i + 1,
            'numeric': (today + timedelta(days=i)).strftime('%d/%m'),
            'day_name': (today + timedelta(days=i)).strftime('%A')[:3],
            'iso_date': (today + timedelta(days=i)).isoformat()
        }
        for i in range(7)
    ]

    # Get showtimes for selected date
    showtimes = Showtime.objects.filter(
        movie=movie,
        room__theater=theater,
        show_date=selected_date
    ).select_related('room', 'room__theater').order_by('room__room_number', 'start_time')

    # Group showtimes by room and check availability
    showtimes_by_room = defaultdict(list)
    for showtime in showtimes:
        # Lấy danh sách ghế đã bán (có ticket với status là paid)
        sold_seats = Ticket.objects.filter(
            showtime=showtime,
            status='paid'
        ).values_list('seats__id', flat=True)
        
        # Cập nhật reserved_seats chỉ với các ghế đã bán
        showtime.reserved_seats = list(sold_seats)
        
        # Check if showtime is full
        total_seats = showtime.room.total_seats
        reserved_seats = len(showtime.reserved_seats) if showtime.reserved_seats else 0
        showtime.is_full = reserved_seats >= total_seats
        
        # Add to room group
        showtimes_by_room[showtime.room].append(showtime)

    # Get selected showtime if any
    selected_showtime_id = request.GET.get('showtime')

    context = {
        'movie': movie,
        'theater': theater,
        'days': days,
        'selected_date': selected_date,
        'showtimes_by_room': dict(showtimes_by_room),
        'selected_showtime_id': selected_showtime_id
    }

    # Handle AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'partials/showtimes_list.html', context)

    # Regular request - return full page
    return render(request, 'ticket-booking.html', context)

def seat_sel_view(request, showtime_id):
    try:
        showtime = get_object_or_404(Showtime, id=showtime_id)
        # Get all seats for the room
        seats = Seat.objects.filter(room=showtime.room).select_related('seat_type')
        # Get all seat types
        seat_types = SeatType.objects.all()
        
        # Serialize data to JSON
        seats_json = serialize('json', seats, fields=('row', 'column', 'seat_type', 'is_active'))
        seat_types_json = serialize('json', seat_types, fields=('name', 'price_multiplier'))
        reserved_seats_json = json.dumps(list(sold_seats))

        context = {
            'showtime': showtime,
            'seats_json': seats_json,
            'seat_types_json': seat_types_json,
            'reserved_seats_json': reserved_seats_json,
            # Keep original querysets for legend rendering if needed
            'seat_types': seat_types, 
        }
        return render(request, 'seat_selection/seat_sel.html', context)
    except Showtime.DoesNotExist:
        return HttpResponse("Invalid showtime")

def select_theater(request):
    if request.method == 'POST':
        theater_id = request.POST.get('theater')
        if theater_id:
            try:
                theater = get_object_or_404(Theater, id=theater_id)
                request.session['selected_theater'] = theater.id
                request.session.modified = True
                return JsonResponse({
                    'success': True,
                    'theater': {
                        'id': theater.id,
                        'name': theater.name,
                        'address': theater.address,
                        'province': extract_province(theater.address)
                    }
                })
            except Theater.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Rạp không tồn tại.'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        return JsonResponse({'success': False, 'error': 'Thiếu thông tin rạp.'}, status=400)
    return JsonResponse({'success': False, 'error': 'Phương thức không được hỗ trợ.'}, status=405)

@require_POST
@csrf_exempt
def create_ticket(request):
    try:
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
            
        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            
        showtime_id = data.get('showtime_id')
        seats = data.get('seats', [])
        payment_method = data.get('payment_method', 'bank')
        
        # Validate required fields
        if not showtime_id:
            return JsonResponse({'error': 'Missing showtime_id'}, status=400)
        if not seats:
            return JsonResponse({'error': 'No seats selected'}, status=400)
            
        try:
            showtime = Showtime.objects.get(id=showtime_id)
        except Showtime.DoesNotExist:
            return JsonResponse({'error': 'Showtime not found'}, status=404)
            
        # Calculate total price based on seats and seat types
        total_price = 0
        selected_seats = []
        for seat_id in seats:
            try:
                seat = Seat.objects.get(id=seat_id)
                seat_price = showtime.price * seat.seat_type.price_multiplier
                total_price += seat_price
                selected_seats.append(seat)
            except Seat.DoesNotExist:
                return JsonResponse({'error': f'Seat {seat_id} not found'}, status=404)
        
        # Create new ticket with pending status
        ticket = Ticket.objects.create(
            showtime=showtime,
            user=request.user,
            status='pending',
            price=total_price
        )
        
        # Add seats to ticket
        ticket.seats.set(selected_seats)
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=request.user,
            ticket=ticket,
            amount=total_price,
            payment_method=payment_method,
            status='pending'
        )
        
        # Generate QR code for the ticket
        qr_data = f"TICKET-{ticket.id}-{transaction.transaction_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        
        # Save QR code to ticket
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        ticket.qr_code.save(f"ticket_{ticket.id}.png", ContentFile(buffer.getvalue()), save=True)
        buffer.close()
        
        # Lên lịch xóa ticket sau 20 phút nếu chưa thanh toán
        delete_unpaid_tickets.apply_async(args=[], countdown=20*60)  # 20 phút = 20 * 60 giây
        
        return JsonResponse({
            'success': True,
            'ticket_id': ticket.id,
            'transaction_id': transaction.transaction_id,
            'amount': total_price,
            'qr_code_url': ticket.qr_code.url if ticket.qr_code else None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get date range for report
    today = datetime.now().date()
    start_date = request.GET.get('start_date', (today - timedelta(days=30)).isoformat())
    end_date = request.GET.get('end_date', today.isoformat())

    try:
        start_date = datetime.fromisoformat(start_date).date()
        end_date = datetime.fromisoformat(end_date).date()
    except ValueError:
        start_date = today - timedelta(days=30)
        end_date = today

    # Get basic stats
    total_users = User.objects.count()
    total_movies = Movie.objects.count()
    total_theaters = Theater.objects.count()

    # Get ticket stats for date range
    tickets_in_range = Ticket.objects.filter(
        purchase_date__date__range=[start_date, end_date]
    )
    total_tickets = tickets_in_range.count()
    total_revenue = tickets_in_range.aggregate(
        total=Sum('price')
    )['total'] or 0

    # Get recent activities
    recent_activities = get_recent_activities()

    context = {
        'total_users': total_users,
        'total_movies': total_movies,
        'total_theaters': total_theaters,
        'total_tickets': total_tickets,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date,
        'recent_activities': recent_activities
    }
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(is_admin)
def admin_movies(request):
    movies = Movie.objects.all().order_by('-release_date')
    return render(request, 'admin/movies.html', {'movies': movies})

@user_passes_test(is_admin)
def admin_theaters(request):
    theaters = Theater.objects.all().order_by('name')
    return render(request, 'admin/theaters.html', {'theaters': theaters})

@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/users.html', {'users': users})

@user_passes_test(is_admin)
def admin_promotions(request):
    promotions = Promotion.objects.all().order_by('-created_at')
    return render(request, 'admin/promotions.html', {'promotions': promotions})

@user_passes_test(is_admin)
def admin_reports(request):
    # Get date range for report
    today = datetime.now().date()
    start_date = request.GET.get('start_date', (today - timedelta(days=30)).isoformat())
    end_date = request.GET.get('end_date', today.isoformat())

    try:
        start_date = datetime.fromisoformat(start_date).date()
        end_date = datetime.fromisoformat(end_date).date()
    except ValueError:
        start_date = today - timedelta(days=30)
        end_date = today

    # Get ticket data for the date range
    tickets = Ticket.objects.filter(
        purchase_date__date__range=[start_date, end_date]
    )

    # Calculate daily revenue
    daily_revenue = tickets.values('purchase_date__date').annotate(
        total=Sum('price')
    ).order_by('purchase_date__date')

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'daily_revenue': daily_revenue,
    }
    return render(request, 'admin/reports.html', context)

@user_passes_test(is_admin)
def admin_content(request):
    banners = Banner.objects.all().order_by('-created_at')
    faqs = FAQ.objects.all().order_by('order')
    return render(request, 'admin/content.html', {
        'banners': banners,
        'faqs': faqs
    })

def get_recent_activities():
    # This is a placeholder function that should be implemented based on your activity tracking system
    # You might want to create a separate model for activity logging
    activities = []
    
    # Get recent ticket purchases
    recent_tickets = Ticket.objects.select_related(
        'user', 'showtime__movie'
    ).order_by('-purchase_date')[:5]
    
    for ticket in recent_tickets:
        activities.append({
            'type': 'ticket_purchase',
            'user': ticket.user.get_full_name() or ticket.user.username,
            'movie': ticket.showtime.movie.title,
            'date': ticket.purchase_date
        })
    
    # Get recent user registrations
    recent_users = User.objects.order_by('-date_joined')[:5]
    for user in recent_users:
        activities.append({
            'type': 'user_registration',
            'user': user.get_full_name() or user.username,
            'date': user.date_joined
        })
    
    # Sort all activities by date
    activities.sort(key=lambda x: x['date'], reverse=True)
    return activities[:10]  # Return only the 10 most recent activities

@user_passes_test(is_admin)
def manage_showtimes(request):
    theaters = Theater.objects.all().order_by('name')
    movies = Movie.objects.filter(
        release_date__lte=timezone.now() + timedelta(days=7)
    ).order_by('title')
    
    return render(request, 'admin/manage_showtimes.html', {
        'theaters': theaters,
        'movies': movies
    })

@require_POST
@csrf_exempt
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

def theater_info(request, theater_id=None):
    # If no theater_id is provided, check if there's a selected theater in session
    if not theater_id:
        if 'selected_theater' in request.session:
            theater_id = request.session['selected_theater']
        else:
            messages.warning(request, 'Vui lòng chọn rạp chiếu trước')
            return redirect('home')
    
    try:
        # Get the theater object
        theater = get_object_or_404(Theater, id=theater_id)
        
        # Get all rooms in this theater
        rooms = Room.objects.filter(theater=theater).order_by('room_number')
        
        # Get today's date
        today = datetime.now().date()
        
        # Get all showtimes for today in this theater
        showtimes = Showtime.objects.filter(
            room__theater=theater,
            show_date=today
        ).select_related('movie', 'room').order_by('room__room_number', 'start_time')
        
        # Group showtimes by room
        showtimes_by_room = defaultdict(list)
        for showtime in showtimes:
            showtimes_by_room[showtime.room].append(showtime)
        
        # Get theater's address components
        address_parts = [part.strip() for part in theater.address.split(',')]
        province = extract_province(theater.address)
        
        context = {
            'theater': theater,
            'rooms': rooms,
            'showtimes_by_room': dict(showtimes_by_room),
            'address_parts': address_parts,
            'province': province,
            'today': today
        }
        
        return render(request, 'theater_intro.html', context)
        
    except Exception as e:
        messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
        return redirect('home')

@login_required
def showtime_management(request):
    if not request.user.is_staff:
        return redirect('home')
        
    movies = Movie.objects.all()
    theaters = Theater.objects.all()
    rooms = Room.objects.all()
    showtimes = Showtime.objects.all().select_related('movie', 'room', 'room__theater')
    
    context = {
        'movies': movies,
        'theaters': theaters,
        'rooms': rooms,
        'showtimes': showtimes,
    }
    return render(request, 'management/showtimes.html', context)

def edit_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        movie.title = request.POST.get('title')
        movie.genre = request.POST.get('genre')
        movie.director = request.POST.get('director')
        movie.actor = request.POST.get('actor')
        movie.duration = request.POST.get('duration')
        movie.release_date = request.POST.get('release_date')
        movie.language = request.POST.get('language')
        movie.description = request.POST.get('description')
        movie.trailer_url = request.POST.get('trailer_url')
        movie.status = request.POST.get('status')
        if request.FILES.get('poster'):
            movie.poster = request.FILES['poster']
        movie.save()
        return redirect('admin_movies')
    return render(request, 'admin/edit_movie.html', {'movie': movie})

@csrf_exempt
def add_movie(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        genre = request.POST.get('genre')
        duration = request.POST.get('duration')
        release_date = request.POST.get('release_date')
        description = request.POST.get('description')
        director = request.POST.get('director')
        actor = request.POST.get('actor')
        language = request.POST.get('language')
        trailer_url = request.POST.get('trailer_url')
        status = request.POST.get('status', 'coming_soon')
        poster = request.FILES.get('poster')
        poster_url = ''
        if poster:
            poster_dir = os.path.join(settings.MEDIA_ROOT, 'posters')
            os.makedirs(poster_dir, exist_ok=True)
            poster_path = os.path.join('posters', poster.name)
            full_path = os.path.join(settings.MEDIA_ROOT, poster_path)
            with open(full_path, 'wb+') as destination:
                for chunk in poster.chunks():
                    destination.write(chunk)
            poster_url = settings.MEDIA_URL + 'posters/' + poster.name
        movie = Movie.objects.create(
            title=title,
            genre=genre,
            duration=duration,
            release_date=release_date,
            description=description,
            director=director,
            actor=actor,
            language=language,
            trailer_url=trailer_url,
            status=status,
            poster_url=poster_url,
        )
        return JsonResponse({'success': True, 'movie_id': movie.id})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@require_POST
@csrf_exempt
def delete_movie(request, movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
        movie.delete()
        return JsonResponse({'success': True})
    except Movie.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Movie not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
@csrf_exempt
def toggle_movie_status(request, movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
        # Chuyển trạng thái: now_showing <-> archived <-> coming_soon
        if movie.status == 'now_showing':
            movie.status = 'archived'
        elif movie.status == 'archived':
            movie.status = 'coming_soon'
        else:
            movie.status = 'now_showing'
        movie.save()
        return JsonResponse({'success': True, 'new_status': movie.status})
    except Movie.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Movie not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)