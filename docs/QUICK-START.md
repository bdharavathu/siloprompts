# SiloPrompts Quick Start Guide

## Get Running in 2 Minutes

### Option 1: Docker (Recommended)
```bash
docker run -d -p 5002:5000 -v ./prompts:/app/prompts bdharavathu/siloprompts
```
Open [http://localhost:5002](http://localhost:5002)

### Option 2: Local
```bash
pip install -r requirements.txt
export PROMPTS_DIR=./prompts DATA_DIR=./data
python app.py
```
Open [http://localhost:5000](http://localhost:5000)

---

## Using the Web UI

### Browse & Search
- **Sidebar** shows all categories with prompt counts
- **Category pills** at the top filter the grid
- **Tags** below categories let you filter across categories (e.g., show all "python" prompts)
- **Search** (press `⌘K`) finds prompts by keyword
- **Sort** using the ☰ button — by name, date, or size

### Copy a Prompt
1. Click a prompt card to open it
2. Each section has a **📋 Copy** button
3. Paste into ChatGPT, Claude, Gemini, or any AI platform

### Favorite Prompts
- Click **☆** next to any section to favorite it
- Click **★ Favorites** in the sidebar to see all your favorites
- Favorites are stored in your browser (no server needed)

### Create a Prompt
1. Click **+ New Prompt**
2. Fill in title, category, tags
3. Add sections — each section is one prompt
4. Click **Save**

### Import a Prompt
1. Click **↓ Import**
2. Select a `.md` file from your computer
3. Choose a category
4. Click **Upload**

### Export a Prompt
1. Open a prompt card
2. Click **↑ Download** to save as `.md`

### Edit & Delete
- Open a prompt → click **Edit** to modify sections, tags, title
- Click **Delete** to remove (with option to clean up empty categories)

---

## Prompt File Format

Prompts are stored as `.md` files in `prompts/<category>/`:

```markdown
# Code Review Prompts
Tags: python, security, best-practices

## General Code Review

​```
Review the following code for:
- Bug risks and logic errors
- Security vulnerabilities
- Performance improvements

[PASTE YOUR CODE HERE]
​```

## Security-Focused Review

​```
Perform a security audit of this code...
​```
```

**Structure:**
- `# Title` — File title (shown on cards)
- `Tags: ...` — Comma-separated, used for filtering
- `## Section` — Each section is a separate prompt
- Code blocks contain the prompt text users copy

---

## CLI Tool

For terminal users:

```bash
python prompt-cli.py list                        # List all categories
python prompt-cli.py search "debug"              # Search prompts
python prompt-cli.py show coding/code-review.md  # View a prompt file
python prompt-cli.py sections coding/debugging.md # List sections
python prompt-cli.py copy coding/debugging.md 0  # Copy to clipboard
```

---

## What's Included

| Category | What's Inside |
|----------|---------------|
| **coding/** | Code review, debugging, generation |
| **writing/** | Blog posts, documentation, emails |
| **analysis/** | Data analysis, comparisons, trends |
| **creative/** | Brainstorming, problem-solving |
| **productivity/** | Planning, prioritization, learning |
| **instructions/** | Task instructions, workflows |

---

## Next Steps

- Browse the included prompts to see what's available
- Create your first custom prompt from the web UI
- Set up tags to organize prompts your way
- Favorite the prompts you use most often
- Check out [API.md](API.md) if you want to integrate programmatically
