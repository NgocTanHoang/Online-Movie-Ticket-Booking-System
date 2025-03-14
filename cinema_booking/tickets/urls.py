from django.contrib import admin
from django.urls import path, include
from .views import LoginClass , home_view


urlpatterns = [
   
    path('login/', LoginClass.as_view(), name='login'),
    path('', home_view, name='home'),
   
]
