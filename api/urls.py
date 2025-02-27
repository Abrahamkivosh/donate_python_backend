from django.urls import path
from .views import train, predict

urlpatterns = [
    path('train/', train, name='train'),
    path('predict/', predict, name='predict'),
]
