from django import forms
from django.contrib.auth.models import User
from .models import Project

# Form đăng ký
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

# Form nhập URL để phân tích
class AnalyzeURLForm(forms.Form):
    url = forms.URLField(label='Enter website URL', max_length=500)

# Form import file cấu hình
class ImportFileForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'config_file']
