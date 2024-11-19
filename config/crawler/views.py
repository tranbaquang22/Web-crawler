from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .forms import RegisterForm, AnalyzeURLForm, ImportFileForm
from .models import Project, Dependency, AnalyzedURL, WebAsset
from .crawler_utils import (
    parse_config_file,
    parse_maven_file,
    parse_gradle_file,
    fetch_web_assets,
    fetch_github_dependencies
)
from django.contrib.auth.decorators import login_required
import requests
@login_required
# Trang chủ
def index(request):
    # Lấy tất cả các dependencies từ database
    dependencies = Dependency.objects.select_related('project').all()
    
    # Lấy tất cả các URL đã phân tích
    analyzed_urls = AnalyzedURL.objects.prefetch_related('assets').all()
    
    # Tạo context để truyền dữ liệu vào template
    context = {
        'dependencies': dependencies,  # Toàn bộ các dependency
        'analyzed_urls': analyzed_urls,  # Tất cả các URL đã phân tích
    }
    return render(request, 'crawler/index.html', context)

# Đăng ký người dùng mới
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'crawler/register.html', {'form': form})

# Đăng nhập
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'crawler/login.html', {'form': form})

# Đăng xuất
def logout_view(request):
    logout(request)
    return redirect('login')

# Trang phân tích file
@login_required
def analyze_file_view(request):
    if request.method == 'POST':
        file = request.FILES.get('config_file')
        project_name = request.POST.get('project_name')

        if file:
            # Tạo project
            project = Project.objects.create(name=project_name, config_file=file)
            file_path = project.config_file.path

            # Phân tích file
            dependencies = []
            if file.name.endswith('.json'):
                dependencies = parse_config_file(file_path)
            elif file.name.endswith('.xml'):
                dependencies = parse_maven_file(file_path)
            elif file.name.endswith('.gradle'):
                dependencies = parse_gradle_file(file_path)
            elif file.name.endswith('.txt'):
                dependencies = parse_config_file(file_path)

            # Lưu dependencies vào database
            for dep in dependencies:
                Dependency.objects.create(
                    project=project,
                    name=dep['name'],
                    version=dep['version'],
                    install_command=dep['install_command']
                )

            return render(request, 'crawler/analysis_result.html', {
                'dependencies': dependencies,
                'result_type': 'file'
            })
    return render(request, 'crawler/analyze_file.html')

# Trang phân tích URL
@login_required
def analyze_url_view(request):
    if request.method == 'POST':
        form = AnalyzeURLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            assets = fetch_web_assets(url)

            # Lưu URL vào cơ sở dữ liệu
            analyzed_url = AnalyzedURL.objects.create(url=url)

            # Lưu từng loại tài nguyên vào cơ sở dữ liệu
            for css in assets.get('css_links', []):
                WebAsset.objects.create(url=analyzed_url, asset_type="CSS", link=css)
            for js in assets.get('js_links', []):
                WebAsset.objects.create(url=analyzed_url, asset_type="JavaScript", link=js)
            for img in assets.get('image_links', []):
                WebAsset.objects.create(url=analyzed_url, asset_type="Image", link=img)
            for favicon in assets.get('favicon_links', []):
                WebAsset.objects.create(url=analyzed_url, asset_type="Favicon", link=favicon)

            # Truyền dữ liệu vào template hiển thị kết quả
            return render(request, 'crawler/analysis_result1.html', {
                'url': url,
                'assets': assets,
                'result_type': 'url'
            })
    else:
        form = AnalyzeURLForm()
    return render(request, 'crawler/analyze_url.html', {'form': form})

# Trang phân tích GitHub repository
@login_required
def analyze_github_view(request):
    if request.method == 'POST':
        repo_url = request.POST.get('repo_url')
        dependencies = fetch_github_dependencies(repo_url)

        # Crawl từng file cấu hình trong repository
        detailed_dependencies = []
        for dep in dependencies:
            if 'raw_url' in dep:
                response = requests.get(dep['raw_url'])
                if response.status_code == 200:
                    content = response.text
                    if dep['file_name'] == 'package.json':
                        detailed_dependencies.extend(parse_config_file(content))
                    elif dep['file_name'] == 'pom.xml':
                        detailed_dependencies.extend(parse_maven_file(content))
                    elif dep['file_name'] == 'build.gradle':
                        detailed_dependencies.extend(parse_gradle_file(content))
                else:
                    print(f"Failed to fetch {dep['raw_url']}, Status Code: {response.status_code}")

        return render(request, 'crawler/analysis_result.html', {
            'dependencies': detailed_dependencies,
            'result_type': 'github'
        })
    return render(request, 'crawler/analyze_github.html')

# Phân tích file trực tiếp từ request POST
def analyze_file(request):
    return analyze_file_view(request)

# Phân tích URL trực tiếp từ request POST
def analyze_url(request):
    return analyze_url_view(request)

# Phân tích GitHub trực tiếp từ request POST
def analyze_github(request):
    return analyze_github_view(request)