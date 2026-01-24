# Archivos y directorios que Cursor debe ignorar

# Dependencias
node_modules/
.venv/
venv/
env/
__pycache__/
*.pyc
*.pyo

# Build outputs
dist/
build/
*.egg-info/
.next/
out/

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Type checking
.mypy_cache/
.dmypy.json

# OS
.DS_Store
Thumbs.db

# Docker
*.pid

# N8N
n8n_data/

# Git
.git/

# Lock files (opcional - algunos prefieren incluirlos)
# uv.lock
# package-lock.json

# Documentación de negocio - INCLUIR (no ignorar)
# Los archivos en docs/business/ son importantes para el contexto
# Solo ignorar si son extremadamente grandes (>10MB)
# docs/business/assets/pdfs/*.pdf  # Descomentar si PDFs son muy grandes

