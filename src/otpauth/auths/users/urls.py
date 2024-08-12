from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.OTPRequestView.as_view(), name='register'),
    path('verify/', views.VerifyUserView.as_view(), name='verify'),
    path('login/', views.UserLoginView.as_view(), name='login'),
]