# PromptDB - Personal AI Prompt Database

A lightweight, self-hosted web application for storing, searching, and managing your AI prompts across different platforms (ChatGPT, Claude, Perplexity, Gemini, etc.).

![PromptDB Web UI](assets/promptDB_ui.png)

![Prompt Sections View](assets/promptdb_sections.png)

## Features

- 🔍 **Full-text search** with real-time results
- 📋 **One-click copy to clipboard**
- 🏷️ **Category organization** for easy browsing
- 📝 **Markdown-based storage** (git-friendly)
- 🐳 **Docker-ready** for easy deployment
- ☸️ **Kubernetes support** with Helm charts
- 🔐 **Secure** with path traversal protection
- 💾 **100% local** - your prompts stay private

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd promptDB

# Start the application
docker-compose up -d

# Access at http://localhost:5002
```

### Option 2: Docker with Custom Configuration

```bash
# Copy environment example
cp .env.example .env

# Generate a secure secret key
python -c 'import secrets; print(secrets.token_hex(32))'

# Edit .env and update SECRET_KEY with the generated key
# Update paths if needed

# Start the application
docker-compose up -d
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
export PROMPTS_DIR=./prompts
export DATA_DIR=./data

# Run the application
python app.py

# Access at http://localhost:5000
```

## Directory Structure

```
promptDB/
├── app.py                    # Flask application
├── prompt-cli.py             # CLI tool
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container image
├── docker-compose.yml        # Docker setup
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── QUICK-START.md            # Quick start guide
├── Makefile                  # Build automation
├── html_templates/           # HTML templates
├── static/                   # CSS, JS, assets
├── prompts/                  # Your prompt library
│   ├── coding/
│   ├── writing/
│   ├── analysis/
│   ├── creative/
│   └── productivity/
├── prompt_templates/         # Prompt templates
├── data/                     # Application data (git-ignored)
└── helm/                     # Kubernetes deployment
    └── promptdb/
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here  # Generate with: python -c 'import secrets; print(secrets.token_hex(32))'

# Paths (for Docker, use /app/prompts and /app/data)
PROMPTS_DIR=/app/prompts
DATA_DIR=/app/data

# Server Configuration
PORT=5000
```

**Important:** Never commit the `.env` file to version control!

## Usage

### Web Interface

1. **Browse prompts** by category in the sidebar
2. **Search** using keywords (e.g., "debug", "blog post")
3. **Click** on a prompt card to view details
4. **Copy** individual prompt sections with one click
5. **Paste** into your favorite AI platform

### CLI Tool

```bash
# Search for prompts
python prompt-cli.py search "debug"

# List all categories
python prompt-cli.py list

# Show a specific prompt file
python prompt-cli.py show coding/code-review.md

# List sections in a file
python prompt-cli.py sections coding/debugging.md

# Copy a prompt section to clipboard
python prompt-cli.py copy coding/debugging.md 0
```

## Deployment Options

### Docker Compose (Development/Personal Use)

```bash
docker-compose up -d
```

Access at: http://localhost:5002

### Kubernetes with Helm

```bash
# Install with default values
helm install promptdb ./helm/promptdb

# Or customize with your values
helm install promptdb ./helm/promptdb -f my-values.yaml

# Upgrade
helm upgrade promptdb ./helm/promptdb

# Uninstall
helm uninstall promptdb
```

#### Kubernetes Configuration

Edit `helm/promptdb/values.yaml` to customize:

- Replica count
- Resource limits
- Ingress settings
- Persistent volume configuration
- Secret key

Example ingress setup:

```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: promptdb.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: promptdb-tls
      hosts:
        - promptdb.yourdomain.com
```

### Production Deployment

For production use:

1. **Generate a strong secret key:**
   ```bash
   python -c 'import secrets; print(secrets.token_hex(32))'
   ```

2. **Update environment variables:**
   - Set `FLASK_ENV=production`
   - Use the generated secret key
   - Configure proper paths for persistent storage

3. **Set up persistent volumes** for:
   - Prompts directory (can be read-only)
   - Data directory (needs write access)

4. **Configure resource limits** in Kubernetes or Docker

5. **Enable HTTPS** using ingress with TLS

## Adding Your Own Prompts

### Via File System

1. Create a markdown file in the appropriate category:
   ```bash
   # Create a new prompt file
   vim prompts/coding/my-custom-prompts.md
   ```

2. Use this format:
   ```markdown
   # My Custom Prompts

   ## Prompt Name

   Description of what this prompt does.

   ```
   Your prompt text here with [PLACEHOLDERS] for variables.
   ```

   ## Another Prompt

   ```
   Another prompt...
   ```
   ```

3. Restart the application or wait for auto-reload (in development mode)

### Using Git for Version Control

```bash
# Track your changes with git
git add prompts/
git commit -m "Add new prompts for [category]"

# Optional: Push to your remote backup
git push
```

## Security Best Practices

✅ **Implemented:**
- Path traversal protection
- Non-root user in Docker
- Security context in Kubernetes
- Environment-based secrets
- XSS protection with HTML escaping

⚠️ **Important:**
- Never commit `.env` files to version control
- Generate strong secret keys for production
- Use HTTPS in production (via ingress/reverse proxy)
- Keep sensitive prompts in private repositories
- Regularly update dependencies

## API Endpoints

The application provides RESTful API endpoints:

```
GET  /api/categories              # List all categories
GET  /api/prompts                 # List all prompts
GET  /api/prompts/<path>          # Get specific prompt details
GET  /api/search?q=<query>        # Search prompts
GET  /health                      # Health check
```

Example API usage:

```bash
# Search for prompts
curl http://localhost:5000/api/search?q=debug

# Get prompt details
curl http://localhost:5000/api/prompts/coding/code-review.md

# Health check
curl http://localhost:5000/health
```

## Troubleshooting

### Docker Issues

**Problem:** Container won't start
```bash
# Check logs
docker-compose logs -f

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

**Problem:** Port already in use
```bash
# Edit docker-compose.yml and change the port mapping
# Change "5002:5000" to "5003:5000" or another available port
```

### Kubernetes Issues

**Problem:** Pod not starting
```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=promptdb

# Check logs
kubectl logs -l app.kubernetes.io/name=promptdb

# Describe pod for events
kubectl describe pod <pod-name>
```

**Problem:** PersistentVolume not mounting
```bash
# Check PVC status
kubectl get pvc

# Update values.yaml with correct storageClass
# Or use hostPath for development
```

### Application Issues

**Problem:** Prompts not showing
- Check that prompts directory is mounted correctly
- Verify prompts directory contains .md files
- Check application logs for errors

**Problem:** Search not working
- Ensure prompts are in the correct markdown format
- Check file permissions (should be readable)

## Platform Compatibility

Works with all major AI platforms:
- ✅ ChatGPT (OpenAI)
- ✅ Claude (Anthropic)
- ✅ Gemini (Google)
- ✅ Perplexity
- ✅ Any custom LLM interface

## Technology Stack

- **Backend:** Python 3.11, Flask 3.0
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Storage:** Markdown files (git-friendly)
- **Container:** Docker, multi-stage builds
- **Orchestration:** Kubernetes with Helm
- **Server:** Gunicorn (production)

## Roadmap

Future enhancements:

- [ ] Prompt editing in web UI
- [ ] Tags for cross-category organization
- [ ] Favorites/bookmarks
- [ ] Usage history and analytics
- [ ] Export prompts (JSON, PDF)
- [ ] Import from other sources
- [ ] Dark/Light mode toggle
- [ ] Browser extension
- [ ] Mobile-responsive improvements

## License

MIT License - Feel free to use, modify, and distribute

---

**Happy Prompting!** 🚀
