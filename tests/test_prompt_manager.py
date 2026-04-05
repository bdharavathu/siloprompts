import pytest
from app import PromptManager


# --- Empty directory behavior ---

class TestEmptyDirectory:
    def test_get_categories_empty_dir(self, prompt_manager):
        assert prompt_manager.get_categories() == {}

    def test_get_all_prompts_empty_dir(self, prompt_manager):
        assert prompt_manager.get_all_prompts() == []

    def test_search_prompts_empty_dir(self, prompt_manager):
        assert prompt_manager.search_prompts('anything') == []


# --- Tags ---

class TestTags:
    def test_tags_roundtrip(self, prompt_manager, sample_sections):
        prompt_manager.create_prompt('testing', 'tagged', 'Tagged Prompt', sample_sections, tags=['python', 'debug'])
        content = prompt_manager.get_prompt_content('testing/tagged.md')
        assert content['tags'] == ['python', 'debug']

    def test_extract_tags_no_tags_line(self):
        assert PromptManager._extract_tags('# Title\n\n## Section\nContent') == []

    def test_extract_tags_empty_value(self):
        assert PromptManager._extract_tags('# Title\nTags: \n') == []

    def test_extract_tags_single(self):
        assert PromptManager._extract_tags('Tags: python') == ['python']

    def test_extract_tags_multiple_with_whitespace(self):
        assert PromptManager._extract_tags('Tags:  python , debug , testing ') == ['python', 'debug', 'testing']

    def test_extract_tags_mixed_case_lowered(self):
        assert PromptManager._extract_tags('Tags: Python, DEBUG') == ['python', 'debug']


# --- Section parsing ---

class TestSectionParsing:
    def test_parse_sections_with_code_blocks(self, populated_manager):
        content = populated_manager.get_prompt_content('coding/code-review.md')
        sections = content['sections']
        assert len(sections) == 2
        assert sections[0]['title'] == 'General Review'
        assert sections[0]['has_code_block'] is True
        assert 'quality and bugs' in sections[0]['prompt']

    def test_parse_sections_no_code_blocks(self, prompt_manager):
        md = "# Title\n\n## My Section\n\nJust plain text here.\n"
        sections = prompt_manager._parse_sections(md)
        assert len(sections) == 1
        assert sections[0]['has_code_block'] is False
        assert 'plain text' in sections[0]['prompt']

    def test_parse_sections_empty_content(self, prompt_manager):
        sections = prompt_manager._parse_sections('# Title only\n')
        assert sections == []


# --- Create prompt ---

class TestCreatePrompt:
    def test_create_writes_file(self, prompt_manager, sample_sections):
        path = prompt_manager.create_prompt('coding', 'new-prompt', 'New Prompt', sample_sections, tags=['test'])
        assert path == 'coding/new-prompt.md'

        file_path = prompt_manager.prompts_path / 'coding' / 'new-prompt.md'
        assert file_path.exists()

        content = file_path.read_text(encoding='utf-8')
        assert content.startswith('# New Prompt')
        assert 'Tags: test' in content
        assert '## Basic Review' in content

    def test_create_creates_category_dir(self, prompt_manager, sample_sections):
        prompt_manager.create_prompt('newcategory', 'test', 'Test', sample_sections)
        assert (prompt_manager.prompts_path / 'newcategory').is_dir()

    def test_create_duplicate_raises(self, prompt_manager, sample_sections):
        prompt_manager.create_prompt('coding', 'dupe', 'Dupe', sample_sections)
        with pytest.raises(FileExistsError):
            prompt_manager.create_prompt('coding', 'dupe', 'Dupe', sample_sections)


# --- Update prompt ---

class TestUpdatePrompt:
    def test_update_preserves_tags_when_not_provided(self, prompt_manager, sample_sections):
        prompt_manager.create_prompt('coding', 'update-test', 'Original', sample_sections, tags=['keep', 'these'])
        prompt_manager.update_prompt('coding/update-test.md', 'Updated', sample_sections, tags=None)
        content = prompt_manager.get_prompt_content('coding/update-test.md')
        assert content['tags'] == ['keep', 'these']

    def test_update_replaces_tags_when_provided(self, prompt_manager, sample_sections):
        prompt_manager.create_prompt('coding', 'tag-replace', 'Original', sample_sections, tags=['old'])
        prompt_manager.update_prompt('coding/tag-replace.md', 'Updated', sample_sections, tags=['new'])
        content = prompt_manager.get_prompt_content('coding/tag-replace.md')
        assert content['tags'] == ['new']

    def test_update_preserves_description(self, prompt_manager):
        file_path = prompt_manager.prompts_path / 'coding'
        file_path.mkdir(parents=True)
        (file_path / 'desc-test.md').write_text(
            "# Title\n\nThis is a description.\n\n## Section\n\n```\nPrompt text\n```\n",
            encoding='utf-8'
        )
        prompt_manager.update_prompt(
            'coding/desc-test.md', 'Title',
            [{'title': 'Section', 'prompt': 'Updated prompt'}]
        )
        content = prompt_manager.get_prompt_content('coding/desc-test.md')
        assert content['description'] == 'This is a description.'

    def test_update_nonexistent_raises(self, prompt_manager, sample_sections):
        with pytest.raises(FileNotFoundError):
            prompt_manager.update_prompt('nope/missing.md', 'Title', sample_sections)


# --- Delete prompt ---

class TestDeletePrompt:
    def test_delete_removes_file(self, prompt_manager, sample_sections):
        prompt_manager.create_prompt('coding', 'to-delete', 'Delete Me', sample_sections)
        prompt_manager.delete_prompt('coding/to-delete.md')
        assert not (prompt_manager.prompts_path / 'coding' / 'to-delete.md').exists()

    def test_delete_empty_category_cleanup(self, prompt_manager, sample_sections):
        prompt_manager.create_prompt('temporary', 'only-one', 'Only', sample_sections)
        result = prompt_manager.delete_prompt('temporary/only-one.md', delete_empty_category=True)
        assert result['category_deleted'] is True
        assert not (prompt_manager.prompts_path / 'temporary').exists()

    def test_delete_keeps_nonempty_category(self, prompt_manager, sample_sections):
        prompt_manager.create_prompt('coding', 'keep1', 'Keep 1', sample_sections)
        prompt_manager.create_prompt('coding', 'keep2', 'Keep 2', sample_sections)
        result = prompt_manager.delete_prompt('coding/keep1.md', delete_empty_category=True)
        assert result['category_deleted'] is False
        assert (prompt_manager.prompts_path / 'coding').exists()

    def test_delete_nonexistent_raises(self, prompt_manager):
        with pytest.raises(FileNotFoundError):
            prompt_manager.delete_prompt('nope/missing.md')


# --- Path validation / security ---

class TestValidation:
    def test_validate_path_traversal_blocked(self, prompt_manager):
        with pytest.raises((ValueError, RuntimeError)):
            prompt_manager._validate_path('../../etc/passwd')

    def test_validate_filename_valid(self):
        assert PromptManager._validate_filename('my-prompt_1') == 'my-prompt_1'

    def test_validate_filename_rejects_dots(self):
        with pytest.raises(ValueError):
            PromptManager._validate_filename('foo.bar')

    def test_validate_filename_rejects_slashes(self):
        with pytest.raises(ValueError):
            PromptManager._validate_filename('foo/bar')

    def test_validate_filename_rejects_empty(self):
        with pytest.raises(ValueError):
            PromptManager._validate_filename('')


# --- Description extraction ---

class TestDescriptionExtraction:
    def test_extract_description_with_content(self):
        md = "# Title\nTags: test\n\nThis is a description.\n\n## Section\nContent"
        assert PromptManager._extract_description(md) == 'This is a description.'

    def test_extract_description_no_description(self):
        md = "# Title\n\n## Section\nContent"
        assert PromptManager._extract_description(md) == ''


# --- Markdown reconstruction ---

class TestMarkdownReconstruction:
    def test_sections_to_markdown_full(self):
        result = PromptManager._sections_to_markdown(
            'My Title',
            [{'title': 'Prompt 1', 'prompt': 'Do something'}],
            description='A useful collection.',
            tags=['python', 'debug']
        )
        lines = result.split('\n')
        assert lines[0] == '# My Title'
        assert 'Tags: python, debug' in result
        assert 'A useful collection.' in result
        assert '## Prompt 1' in result
        assert 'Do something' in result
