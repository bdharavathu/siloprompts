import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import app as app_module


@pytest.fixture
def prompt_manager(tmp_path):
    return app_module.PromptManager(tmp_path)


@pytest.fixture
def sample_sections():
    return [{'title': 'Basic Review', 'prompt': 'Review this code for bugs and improvements.'}]


@pytest.fixture
def populated_dir(tmp_path):
    coding = tmp_path / 'coding'
    coding.mkdir()
    (coding / 'code-review.md').write_text(
        "# Code Review Prompts\n"
        "Tags: review, quality\n"
        "\n"
        "A collection of code review prompts.\n"
        "\n"
        "## General Review\n"
        "\n"
        "```\n"
        "Review this code for quality and bugs.\n"
        "```\n"
        "\n"
        "## Security Review\n"
        "\n"
        "```\n"
        "Check this code for security vulnerabilities.\n"
        "```\n",
        encoding='utf-8'
    )

    writing = tmp_path / 'writing'
    writing.mkdir()
    (writing / 'blog-post.md').write_text(
        "# Blog Post Prompts\n"
        "\n"
        "## Write a Blog Post\n"
        "\n"
        "```\n"
        "Write a blog post about [TOPIC].\n"
        "```\n",
        encoding='utf-8'
    )

    return tmp_path


@pytest.fixture
def populated_manager(populated_dir):
    return app_module.PromptManager(populated_dir)


@pytest.fixture
def client(tmp_path):
    app_module.app.config['TESTING'] = True
    original = app_module.prompt_manager
    app_module.prompt_manager = app_module.PromptManager(tmp_path)
    with app_module.app.test_client() as c:
        yield c
    app_module.prompt_manager = original


@pytest.fixture
def populated_client(populated_dir):
    app_module.app.config['TESTING'] = True
    original = app_module.prompt_manager
    app_module.prompt_manager = app_module.PromptManager(populated_dir)
    with app_module.app.test_client() as c:
        yield c
    app_module.prompt_manager = original
