from django.urls import path
from .views import home_view
from .views import analytics

urlpatterns = [
    path('', home_view, name='home'),
    path('analytics/', analytics, name="analytics" ),
]