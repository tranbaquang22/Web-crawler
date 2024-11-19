from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),  # Trang chủ
    path('analyze_file/', views.analyze_file, name='analyze_file'),  # Phân tích file
    path('analyze_url/', views.analyze_url, name='analyze_url'),  # Phân tích URL
    path('analyze_github/', views.analyze_github, name='analyze_github'),  # Phân tích GitHub
    path('register/', views.register, name='register'),  # Đăng ký
    path('login/', views.login_view, name='login'),  # Đăng nhập
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Đăng xuất
]
