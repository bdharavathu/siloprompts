# SiloPrompts

**Personal AI prompt database — organize, search, and copy your prompts.**

![SiloPrompts Walkthrough](https://raw.githubusercontent.com/bdharavathu/siloprompts/main/assets/siloprompts-walkthrough.gif)

---

## Install in 10 seconds

=== "pip"

    ```bash
    pip install siloprompts
    siloprompts
    ```

=== "Docker"

    ```bash
    docker run -d -p 5002:5000 bdharavathu/siloprompts
    ```

=== "From Source"

    ```bash
    git clone https://github.com/bdharavathu/siloprompts.git
    cd siloprompts
    pip install -e ".[dev,server]"
    siloprompts --open
    ```

---

## Why SiloPrompts?

Every AI interaction starts with a prompt. The ones that actually work — refined through trial and error, containing your proprietary workflows — those are valuable.

Most people store them in scattered chat histories, random notes, or nowhere at all. Cloud prompt managers exist, but they require uploading your prompts to someone else's server.

**SiloPrompts keeps your prompts on your machine.** Open source. No cloud. No accounts. No data leaving your environment.

[Read more :material-arrow-right:](why-siloprompts.md){ .md-button }

---

## Features

| | Feature | Description |
|---|---------|-------------|
| :pencil2: | **Full CRUD** | Create, edit, delete prompts from the web UI |
| :mag: | **Full-text search** | Real-time results with `Cmd+K` shortcut |
| :clipboard: | **One-click copy** | Find the prompt, copy, paste into any AI tool |
| :label: | **Tags** | Cross-category organization with multi-select filtering |
| :star: | **Favorites** | Bookmark specific prompt sections for quick access |
| :package: | **Import/Export** | Upload `.md` files, download backups as ZIP |
| :art: | **Dark/Light mode** | Glassmorphism theme with automatic switching |
| :lock: | **100% local** | Markdown files, git-friendly, no database |
| :whale: | **Docker-ready** | Kubernetes and Helm chart included |

---

## How it works

Prompts are stored as plain markdown files on your machine:

```
~/.siloprompts/prompts/
  coding/
    code-review.md
    debugging.md
  writing/
    blog-post.md
```

No database, no proprietary format. The files are git-friendly, human-readable, and portable. SiloPrompts wraps a clean web UI around this folder structure.

---

## Who it's for

- **Developers** who use AI for code review, debugging, and architecture decisions
- **Content creators** who maintain prompt templates for writing and brainstorming
- **Analysts** who build repeatable prompts for data analysis and research
- **Anyone** who talks to AI regularly and wants their best prompts organized

---

<div style="text-align: center; padding: 2rem 0;">
  <a href="quick-start/" class="md-button md-button--primary">Get Started</a>
  <a href="https://github.com/bdharavathu/siloprompts" class="md-button">View on GitHub</a>
</div>
