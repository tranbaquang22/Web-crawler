from django.db import models

# Bảng lưu trữ thông tin dự án
class Project(models.Model):
    name = models.CharField(max_length=255)  # Tên dự án
    description = models.TextField(null=True, blank=True)  # Mô tả dự án
    config_file = models.FileField(upload_to='configs/', null=True, blank=True)  # File cấu hình (package.json, requirements.txt)

    def __str__(self):
        return self.name

# Bảng lưu thông tin chi tiết dependencies
class Dependency(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='dependencies')  # Liên kết đến project
    name = models.CharField(max_length=255)  # Tên package/library
    version = models.CharField(max_length=50, null=True, blank=True)  # Phiên bản
    install_command = models.CharField(max_length=255, null=True, blank=True)  # Cách cài đặt
    documentation_url = models.URLField(null=True, blank=True)  # URL tài liệu (nếu có)
    dependency_info = models.TextField(null=True, blank=True)  # Thông tin phụ thuộc (nếu có)

    def __str__(self):
        return f"{self.name} ({self.version})"

class AnalyzedURL(models.Model):
    url = models.URLField()  # URL đã phân tích
    analyzed_at = models.DateTimeField(auto_now_add=True)  # Thời gian phân tích

    def __str__(self):
        return self.url


class WebAsset(models.Model):
    url = models.ForeignKey(AnalyzedURL, on_delete=models.CASCADE, related_name="assets")  # URL liên kết
    asset_type = models.CharField(max_length=20)  # Loại tài nguyên (CSS, JS, Image, Favicon)
    link = models.URLField()  # Đường dẫn tới tài nguyên

    def __str__(self):
        return f"{self.asset_type}: {self.link}"