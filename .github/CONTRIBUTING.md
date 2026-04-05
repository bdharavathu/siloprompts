# Contributing to SiloPrompts

Thanks for your interest in contributing! SiloPrompts is open source and welcomes contributions.

## Quick Start

```bash
git clone https://github.com/bdharavathu/siloprompts.git
cd siloprompts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_ENV=development PROMPTS_DIR=./prompts DATA_DIR=./data
python app.py
```

Open `http://localhost:5000` — you're ready to develop.

## Running Tests

```bash
pytest tests/ -v
```

All tests must pass before submitting a PR.

## How to Contribute

### Reporting Bugs

- Check [existing issues](https://github.com/bdharavathu/siloprompts/issues) first
- Include steps to reproduce, expected vs actual behavior
- Include browser/OS/Docker version if relevant

### Suggesting Features

- Open an issue with the `enhancement` label
- Describe the use case, not just the solution
- Keep SiloPrompts' philosophy in mind: private, local-first, simple

### Submitting Code

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Add or update tests if applicable
4. Run `pytest tests/ -v` — all tests must pass
5. Submit a pull request

### Code Style

- Python: follow existing patterns in `app.py`
- JavaScript: vanilla JS, no frameworks, no build tools
- CSS: use existing CSS variables (`var(--primary)`, `var(--card-bg)`, etc.)
- Keep it simple — minimal dependencies, no unnecessary abstractions

## Project Philosophy

SiloPrompts is private, self-hosted, and simple by design. Contributions should align with:

- **No cloud dependencies** — everything runs locally
- **No accounts or auth** — it's a personal/team tool
- **No database** — markdown files are the storage layer
- **Minimal dependencies** — stdlib over third-party when possible
- **End-user satisfaction** — every feature should make the user's life easier

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
