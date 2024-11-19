from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
urlpatterns = [
    path('admin/', admin.site.urls),  # Đường dẫn vào trang admin
    path('accounts/login/', LoginView.as_view(template_name='crawler/login.html'), name='login'),
    path('', include('crawler.urls')),  # Đường dẫn vào app crawler
]

# Cấu hình đường dẫn cho file tĩnh (upload file cấu hình)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
