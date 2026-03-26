# SiloPrompts Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1️⃣ Browse Your Prompts

```bash
# List all available prompts
python3 prompt-cli.py list

# Or browse manually
cd prompts/coding
cat code-review.md
```

### 2️⃣ Search for What You Need

```bash
# Search by keyword
python3 prompt-cli.py search "debug"
python3 prompt-cli.py search "blog post"
python3 prompt-cli.py search "security"
```

### 3️⃣ Copy & Use

```bash
# Method 1: View sections in a file
python3 prompt-cli.py sections coding/debugging.md

# Method 2: Copy to clipboard (requires: pip install pyperclip)
python3 prompt-cli.py copy coding/debugging.md 0

# Method 3: Manual copy
# Open the file, copy the prompt, replace [PLACEHOLDERS], paste to AI
```

---

## 📁 What's Inside

| Category | Description | Example Prompts |
|----------|-------------|-----------------|
| **coding/** | Programming tasks | Code review, debugging, generation |
| **writing/** | Content creation | Blog posts, documentation, emails |
| **analysis/** | Data & research | Data analysis, comparisons, trends |
| **creative/** | Ideation | Brainstorming, problem-solving |
| **productivity/** | Organization | Planning, prioritization, learning |

---

## 💡 Common Use Cases

### Debug a Problem
```bash
python3 prompt-cli.py show coding/debugging.md
# Copy "General Bug Diagnosis" prompt
# Replace [PLACEHOLDERS] with your code and error
# Paste to ChatGPT/Claude/Gemini/Perplexity
```

### Write a Blog Post
```bash
python3 prompt-cli.py show writing/content-creation.md
# Copy "Blog Post Writing" prompt
# Fill in topic, audience, key points
# Get AI to write your post
```

### Plan a Project
```bash
python3 prompt-cli.py show productivity/planning.md
# Copy "Project Planning" prompt
# Describe your project
# Get structured plan with milestones
```

---

## ✏️ Add Your Own Prompts

### Option 1: Create New File
```bash
# Copy the template
cp templates/prompt-template.md prompts/coding/my-custom-prompts.md

# Edit with your favorite editor
code prompts/coding/my-custom-prompts.md
```

### Option 2: Add to Existing File
```bash
# Edit any existing file
code prompts/coding/code-review.md

# Add new section with ## header
## My Custom Review

```
[Your prompt here]
```
```

---

## 🔐 Security & Backup

### Option 1: Git (Recommended)
```bash
# Initialize git
git init
git add .
git commit -m "Initial prompt database"

# Add remote backup (optional)
git remote add origin https://github.com/yourusername/my-prompts.git
git push -u origin main
```

### Option 2: Cloud Sync
Move the folder to Dropbox/iCloud/Google Drive for automatic backup.

### Option 3: Encryption
```bash
# For sensitive prompts
brew install git-crypt  # macOS
git-crypt init
```

---

## 🎯 Next Steps

- [ ] Try searching for a prompt: `python3 prompt-cli.py search "your topic"`
- [ ] Browse a category: `ls prompts/coding`
- [ ] Use a prompt with ChatGPT/Claude
- [ ] Add your first custom prompt
- [ ] Set up git for versioning
- [ ] Explore advanced options in `docs/ADVANCED-SETUP.md`

---

## 🆘 Need Help?

**CLI Commands:**
```bash
python3 prompt-cli.py --help           # Show all commands
python3 prompt-cli.py search --help    # Help for search
```

**Common Issues:**

Q: "python3: command not found"
A: Install Python from python.org or use `python` instead

Q: "How do I copy prompts?"
A: Install pyperclip: `pip install pyperclip`
   Or just view and manually copy

Q: "Can I edit prompts?"
A: Yes! All prompts are in `prompts/` - edit with any text editor

---

## 🚀 Want More?

Check out `docs/ADVANCED-SETUP.md` for:
- Web interface with Docker
- Browser extension
- API server
- Team collaboration setup

**Start simple, expand when needed!**
