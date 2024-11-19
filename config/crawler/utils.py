import json
from .models import Dependency

def analyze_project_file(project):
    if project.config_file:
        with open(project.config_file.path, 'r', encoding='utf-8') as file:
            content = file.read()
            if 'package.json' in project.config_file.name:
                data = json.loads(content)
                for name, version in data.get('dependencies', {}).items():
                    Dependency.objects.create(
                        project=project,
                        name=name,
                        version=version,
                        install_command=f"npm install {name}@{version}"
                    )
