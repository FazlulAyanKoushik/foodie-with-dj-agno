"""
URL configuration for chat app.
"""
from django.urls import path
from chat import views

app_name = 'chat'

urlpatterns = [
    path('<uuid:restaurant_uid>/', views.ChatAPIView.as_view(), name='chat'),
]
