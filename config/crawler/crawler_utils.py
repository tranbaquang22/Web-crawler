import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import xml.etree.ElementTree as ET
import chardet

def parse_config_file(file_path):
    dependencies = []
    try:
        # Đoán mã hóa của file
        with open(file_path, 'rb') as raw_file:
            raw_data = raw_file.read()
            result = chardet.detect(raw_data)  # Phát hiện mã hóa
            encoding = result['encoding']
            print(f"Detected file encoding: {encoding}")

        # Đọc file với mã hóa đã phát hiện
        with open(file_path, 'r', encoding=encoding) as file:
            if file_path.endswith('.json'):  # Phân tích package.json
                data = json.load(file)
                print("Parsed JSON data:", data)  # Log dữ liệu JSON
                for dep, version in data.get('dependencies', {}).items():
                    dependencies.append({
                        'name': dep,
                        'version': version,
                        'install_command': f'npm install {dep}@{version}'
                    })
            elif file_path.endswith('.txt'):  # Phân tích requirements.txt
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):  # Bỏ qua dòng trống hoặc comment
                        continue
                    if '==' in line:
                        try:
                            name, version = line.split('==', 1)
                            dependencies.append({
                                'name': name.strip(),
                                'version': version.strip(),
                                'install_command': f'pip install {name.strip()}=={version.strip()}'
                            })
                        except ValueError:
                            print(f"Invalid line format: {line}")
        return dependencies
    except Exception as e:
        print(f"Error reading config file: {e}")
        return []


# Test
dependencies = parse_config_file('./requirements.txt')
print("Dependencies:", dependencies)

# Test
dependencies = parse_config_file('requirements.txt')
print("Dependencies:", dependencies)

# Phân tích file Maven (pom.xml)
def parse_maven_file(file_path):
    dependencies = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Xử lý namespace nếu có
        namespace = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}

        for dep in root.findall(".//ns:dependency" if namespace else ".//dependency", namespaces=namespace):
            group_id = dep.find("ns:groupId" if namespace else "groupId", namespaces=namespace)
            artifact_id = dep.find("ns:artifactId" if namespace else "artifactId", namespaces=namespace)
            version = dep.find("ns:version" if namespace else "version", namespaces=namespace)

            dependencies.append({
                'name': f"{group_id.text}:{artifact_id.text}" if group_id is not None and artifact_id is not None else "Unknown",
                'version': version.text if version is not None else "N/A",
                'install_command': f'mvn install {artifact_id.text if artifact_id is not None else "Unknown"}'
            })
        return dependencies
    except ET.ParseError as e:
        print(f"XML parse error in {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error reading Maven file {file_path}: {e}")
        return []



# Phân tích file Gradle (build.gradle)
def parse_gradle_file(file_path):
    dependencies = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith(('implementation', 'api')) and "'" in line:
                    parts = line.split("'")
                    if len(parts) >= 2:
                        dep = parts[1].split(':')
                        if len(dep) == 3:
                            dependencies.append({
                                'name': f"{dep[0]}:{dep[1]}",
                                'version': dep[2],
                                'install_command': f'gradle build {dep[1]}'
                            })
                        else:
                            print(f"Invalid dependency format in line: {line}")
        return dependencies
    except Exception as e:
        print(f"Error reading Gradle file {file_path}: {e}")
        return []


# Crawl dữ liệu từ URL
def fetch_web_assets(url):
    try:
        # Gửi request GET tới URL
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

        # Kiểm tra nếu request thành công
        if response.status_code == 200:
            # Phân tích cú pháp nội dung HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Lấy các liên kết CSS
            css_links = [
                urljoin(url, link['href']) for link in soup.find_all('link', rel='stylesheet', href=True)
            ]

            # Lấy liên kết favicon
            favicon_links = [
                urljoin(url, link['href']) for link in soup.find_all('link', rel='icon', href=True)
            ] + [
                urljoin(url, link['href']) for link in soup.find_all('link', rel='shortcut icon', href=True)
            ]

            # Lấy các liên kết hình ảnh
            image_links = [
                urljoin(url, img['src']) for img in soup.find_all('img', src=True)
            ]

            # Lấy các liên kết JavaScript
            js_links = [
                urljoin(url, script['src']) for script in soup.find_all('script', src=True)
            ]

            # Trả về thông tin đã thu thập
            return {
                'css_links': css_links,
                'favicon_links': favicon_links,
                'image_links': image_links,
                'js_links': js_links
            }
        else:
            print(f"Failed to fetch data from {url}, Status Code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Crawl thông tin từ GitHub repository
def fetch_github_dependencies(repo_url):
    try:
        api_url = repo_url.replace("github.com", "api.github.com/repos")
        response = requests.get(f"{api_url}/contents")
        if response.status_code == 200:
            files = response.json()
            dependencies = []
            for file in files:
                if file['name'] in ['package.json', 'requirements.txt', 'pom.xml', 'build.gradle']:
                    raw_url = file['download_url']
                    dependencies.append({'file_name': file['name'], 'raw_url': raw_url})
            return dependencies
        else:
            print(f"GitHub API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching GitHub repository: {e}")
        return []
