# Quick Start

## Get running in 30 seconds

=== "pip (Simplest)"

    ```bash
    pip install siloprompts
    siloprompts
    ```

    Open [http://localhost:5000](http://localhost:5000)

    Prompts are stored in `~/.siloprompts/prompts/` by default. 10 starter prompts are included on first run.

    ```bash
    # Custom port and prompts directory
    siloprompts --port 5002 --prompts /path/to/prompts

    # Open browser automatically
    siloprompts --open

    # Show version
    siloprompts --version
    ```

=== "Docker"

    ```bash
    docker run -d -p 5002:5000 bdharavathu/siloprompts
    ```

    Open [http://localhost:5002](http://localhost:5002)

    Mount your own prompts folder for persistence:

    ```bash
    docker run -d -p 5002:5000 -v ./prompts:/app/prompts bdharavathu/siloprompts
    ```

=== "Docker Compose"

    ```bash
    git clone https://github.com/bdharavathu/siloprompts.git
    cd siloprompts
    docker-compose up -d
    ```

    Open [http://localhost:5002](http://localhost:5002)

=== "From Source"

    ```bash
    git clone https://github.com/bdharavathu/siloprompts.git
    cd siloprompts
    pip install -e ".[dev,server]"
    siloprompts --port 5000 --prompts ./prompts --open
    ```

---

## Using the Web UI

### Browse and Search

- **Sidebar** shows all categories with prompt counts
- **Category pills** at the top filter the grid
- **Tags** below categories let you filter across categories
- **Search** (press `Cmd+K`) finds prompts by keyword
- **Sort** using the button — by name, date, or size

### Copy a Prompt

1. Click a prompt card to open it
2. Each section has a **Copy** button
3. Paste into ChatGPT, Claude, Gemini, or any AI platform

### Favorite Prompts

- Click the star next to any section to favorite it
- Click **Favorites** in the sidebar to see all your favorites
- Favorites are stored in your browser

### Create a Prompt

1. Click **+ New Prompt**
2. Fill in title, category, tags
3. Add sections — each section is one prompt
4. Click **Save**

### Import and Export

- **Import**: Click **Import**, select a `.md` file, choose a category
- **Export**: Open a prompt, click **Download** to save as `.md`
- **Backup**: Download all prompts as a ZIP from the API

### Edit and Delete

- Open a prompt, click **Edit** to modify sections, tags, title
- Click **Delete** to remove (with option to clean up empty categories)

---

## Prompt File Format

Prompts are stored as `.md` files in `prompts/<category>/`:

```markdown
# Code Review Prompts
Tags: python, security, best-practices

## General Code Review

Review the following code for:
- Bug risks and logic errors
- Security vulnerabilities
- Performance improvements

[PASTE YOUR CODE HERE]

## Security-Focused Review

Perform a security audit of this code...
```

**Structure:**

- `# Title` — File title (shown on cards)
- `Tags: ...` — Comma-separated, used for filtering
- `## Section` — Each section is a separate prompt
- Code blocks contain the prompt text users copy

---

## What's Included

10 starter prompts ship with SiloPrompts:

| Category | Prompts |
|----------|---------|
| **coding** | Code review, debugging, code generation |
| **writing** | Content creation |
| **analysis** | Data analysis |
| **creative** | Brainstorming |
| **productivity** | Planning |
| **instructions** | Behavior control, output format, response guidelines |

---

## Next Steps

- Browse the included prompts to see what's available
- Create your first custom prompt from the web UI
- Set up tags to organize prompts your way
- Favorite the prompts you use most often
- Check out the [API Reference](api.md) to integrate programmatically
