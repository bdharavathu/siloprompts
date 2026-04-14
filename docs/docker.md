# Docker Deployment

## Quick Start

```bash
docker run -d -p 5002:5000 --name siloprompts bdharavathu/siloprompts
```

Open [http://localhost:5002](http://localhost:5002)

---

## With Persistent Prompts

=== "Mac / Linux"

    ```bash
    mkdir -p ~/siloprompts-data/prompts

    docker run -d -p 5002:5000 \
      -v ~/siloprompts-data/prompts:/app/prompts \
      --name siloprompts \
      bdharavathu/siloprompts
    ```

=== "Windows (PowerShell)"

    ```powershell
    mkdir C:\Users\%USERNAME%\siloprompts-data\prompts

    docker run -d -p 5002:5000 `
      -v C:\Users\%USERNAME%\siloprompts-data\prompts:/app/prompts `
      --name siloprompts `
      bdharavathu/siloprompts
    ```

!!! tip
    Without `-v`, prompts are stored inside the container and lost when the container is removed. Always mount a volume for persistence.

---

## Docker Compose

```bash
git clone https://github.com/bdharavathu/siloprompts.git
cd siloprompts
docker compose up -d
```

Open [http://localhost:5002](http://localhost:5002)

---

## Common Tasks

**View logs:**
```bash
docker logs siloprompts
docker logs -f siloprompts    # follow live
```

**Stop / Start / Remove:**
```bash
docker stop siloprompts
docker start siloprompts
docker rm siloprompts
```

**Update to latest version:**
```bash
docker pull bdharavathu/siloprompts:latest
docker stop siloprompts && docker rm siloprompts
# Re-run the docker run command above
```

**Change port:**
```bash
docker run -d -p 8080:5000 --name siloprompts bdharavathu/siloprompts
# Opens at http://localhost:8080
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMPTS_DIR` | `/app/prompts` | Prompts storage directory |
| `DATA_DIR` | `/app/data` | Application data directory |
| `FLASK_ENV` | `production` | Flask environment |
| `SECRET_KEY` | `dev-key-change-in-production` | Flask secret key |
| `PORT` | `5000` | Server port |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port already in use | Change `-p 5002:5000` to a different port like `-p 8080:5000` |
| Container exits immediately | Run `docker logs siloprompts` to check errors |
| Prompts not persisting | Make sure you're using the `-v` volume mount |
| Permission denied on volume (Linux) | Add `--user $(id -u):$(id -g)` to the run command |
| Windows: "WSL 2 not installed" | Open Docker Desktop settings, enable WSL 2 backend |
