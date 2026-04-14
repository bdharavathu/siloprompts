import pytest
from siloprompts.manager import PromptManager
from siloprompts.web import create_app


@pytest.fixture
def prompt_manager(tmp_path):
    return PromptManager(tmp_path)


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
    return PromptManager(populated_dir)


@pytest.fixture
def client(tmp_path):
    # Place marker to skip default prompts copy in tests
    (tmp_path / '.initialized').touch()
    app = create_app(prompts_dir=str(tmp_path))
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def populated_client(populated_dir):
    app = create_app(prompts_dir=str(populated_dir))
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c
