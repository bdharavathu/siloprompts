# Web UI Guide

## Overview

SiloPrompts provides a clean web interface for managing your AI prompts. This guide covers all features available in the UI.

## Navigation

### Sidebar

The sidebar shows:

- **All Prompts** — view everything
- **Favorites** — your bookmarked prompt sections
- **Categories** — grouped by folder with prompt counts
- **Tags** — filter across categories

### Search

Press `Cmd+K` (Mac) or `Ctrl+K` (Windows/Linux) to open search. Results update in real-time as you type. Search looks through prompt titles, content, and tags.

### Sort

Sort prompts by:

- **Name** — alphabetical
- **Date modified** — most recent first
- **Size** — largest first

---

## Managing Prompts

### Create a Prompt

1. Click **+ New Prompt**
2. Enter a **title** and select a **category** (or create a new one)
3. Add **tags** (comma-separated) for cross-category filtering
4. Add one or more **sections** — each section is a separate prompt with its own title and content
5. Click **Save**

### Edit a Prompt

1. Open a prompt by clicking its card
2. Click **Edit**
3. Modify title, tags, or sections
4. Add or remove sections as needed
5. Click **Save**

### Delete a Prompt

1. Open a prompt
2. Click **Delete**
3. Optionally check "Delete empty category" to clean up the folder if it becomes empty

### Copy a Prompt

1. Open a prompt
2. Each section has a **Copy** button
3. Click it — the prompt text is copied to your clipboard
4. Paste into ChatGPT, Claude, Gemini, Perplexity, or any AI tool

---

## Favorites

Click the star icon next to any prompt section to favorite it. Access all favorites from the **Favorites** section in the sidebar.

Favorites are stored in your browser's local storage — they persist across sessions but are specific to the browser.

---

## Import and Export

### Import a Prompt

1. Click **Import**
2. Select a `.md` file from your computer
3. Choose a target category
4. Click **Upload**

The file must be a valid markdown file (`.md` extension, max 1MB).

### Export a Prompt

1. Open a prompt
2. Click **Download**
3. The prompt is saved as a `.md` file

### Backup and Restore

- **Backup**: `GET /api/backup` downloads all prompts as a ZIP file
- **Restore**: `POST /api/restore` uploads a ZIP backup (supports skip or overwrite modes)

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+K` / `Ctrl+K` | Focus search |
| `Escape` | Close modal / clear search |

---

## Dark and Light Mode

Click the theme toggle in the top-right corner to switch between dark and light mode. Your preference is saved in the browser.
