from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('analytics/', views.analytics, name='analytics'),
    path('register/', views.register, name='register'),
]