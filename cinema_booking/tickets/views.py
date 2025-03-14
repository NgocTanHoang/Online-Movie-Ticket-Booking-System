from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.views import View
from .models import User, Movie, Theater, Room, Showtime, Ticket, Transaction
from .serializers import (UserSerializer, MovieSerializer, TheaterSerializer,
                         RoomSerializer, ShowtimeSerializer, TicketSerializer,
                         TransactionSerializer)
from django.shortcuts import render, redirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer

class LoginClass(View):
    def get(self, request):
        """Hiển thị trang đăng nhập khi nhận yêu cầu GET"""
        return render(request, 'login.html')
    
    def post(self, request):
        """Xử lý đăng nhập khi nhận yêu cầu POST"""
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Xác thực người dùng
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_staff: 
                # login(request, user)
                next_url = request.GET.get('next', 'home')  # Chuyển hướng đến 'home' hoặc URL từ 'next'
                return redirect(next_url)
            # elif user.is_active:  # Nếu là người dùng thông thường
            #     # login(request, user)
            #     url_user = f'/user/{user.username}/'  # Ví dụ: đường dẫn tùy chỉnh cho người dùng
            #     next_url = request.GET.get('next', url_user)
            #     return redirect(next_url)
            # else:
            #     error_message = "Tài khoản không hợp lệ hoặc không có quyền truy cập."
            return render(request, 'login.html', {'error_message': error_message})
        else:
            error_message = "Thông tin đăng nhập không đúng."
            return render(request, 'login.html', {'error_message': error_message})
        

def home_view(request):
    return render(request, 'sign_in.html')