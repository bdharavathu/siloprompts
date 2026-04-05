import io
import zipfile
import pytest


# --- Health ---

class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data


# --- Categories ---

class TestCategories:
    def test_get_categories_empty(self, client):
        resp = client.get('/api/categories')
        assert resp.status_code == 200
        assert resp.get_json() == {}

    def test_get_categories_populated(self, populated_client):
        resp = populated_client.get('/api/categories')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'coding' in data
        assert 'writing' in data


# --- List / Detail ---

class TestPromptsList:
    def test_get_prompts_empty(self, client):
        resp = client.get('/api/prompts')
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_get_prompts_populated(self, populated_client):
        resp = populated_client.get('/api/prompts')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2

    def test_get_prompt_detail(self, populated_client):
        resp = populated_client.get('/api/prompts/coding/code-review.md')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['path'] == 'coding/code-review.md'
        assert len(data['sections']) == 2
        assert data['tags'] == ['review', 'quality']
        assert 'raw' in data

    def test_get_prompt_not_found(self, client):
        resp = client.get('/api/prompts/nope/missing.md')
        assert resp.status_code == 404


# --- Create ---

class TestCreatePrompt:
    def test_create_returns_201(self, client):
        resp = client.post('/api/prompts', json={
            'category': 'testing',
            'filename': 'my-prompt',
            'title': 'My Prompt',
            'sections': [{'title': 'Section 1', 'prompt': 'Do something'}],
            'tags': ['test']
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['path'] == 'testing/my-prompt.md'

    def test_create_missing_field(self, client):
        resp = client.post('/api/prompts', json={
            'category': 'testing',
            'title': 'No Sections'
        })
        assert resp.status_code == 400

    def test_create_duplicate(self, client):
        payload = {
            'category': 'coding',
            'filename': 'dupe',
            'title': 'Dupe',
            'sections': [{'title': 'S', 'prompt': 'P'}]
        }
        client.post('/api/prompts', json=payload)
        resp = client.post('/api/prompts', json=payload)
        assert resp.status_code == 409

    def test_create_invalid_filename(self, client):
        resp = client.post('/api/prompts', json={
            'category': 'coding',
            'filename': 'bad.name',
            'title': 'Bad',
            'sections': [{'title': 'S', 'prompt': 'P'}]
        })
        assert resp.status_code == 400

    def test_create_no_json_body(self, client):
        resp = client.post('/api/prompts', content_type='application/json', data='')
        assert resp.status_code == 400


# --- Update ---

class TestUpdatePrompt:
    def test_update_returns_200(self, populated_client):
        resp = populated_client.put('/api/prompts/coding/code-review.md', json={
            'title': 'Updated Title',
            'sections': [{'title': 'New Section', 'prompt': 'New content'}]
        })
        assert resp.status_code == 200

    def test_update_not_found(self, client):
        resp = client.put('/api/prompts/nope/missing.md', json={
            'title': 'Title',
            'sections': [{'title': 'S', 'prompt': 'P'}]
        })
        assert resp.status_code == 404

    def test_update_missing_field(self, populated_client):
        resp = populated_client.put('/api/prompts/coding/code-review.md', json={
            'title': 'Title Only'
        })
        assert resp.status_code == 400


# --- Delete ---

class TestDeletePrompt:
    def test_delete_returns_200(self, populated_client):
        resp = populated_client.delete('/api/prompts/coding/code-review.md')
        assert resp.status_code == 200

    def test_delete_not_found(self, client):
        resp = client.delete('/api/prompts/nope/missing.md')
        assert resp.status_code == 404


# --- Search ---

class TestSearch:
    def test_search_finds_content(self, populated_client):
        resp = populated_client.get('/api/search?q=security')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['count'] >= 1

    def test_search_no_query(self, client):
        resp = client.get('/api/search')
        assert resp.status_code == 400

    def test_search_empty_query(self, client):
        resp = client.get('/api/search?q=')
        assert resp.status_code == 400

    def test_search_no_results(self, populated_client):
        resp = populated_client.get('/api/search?q=xyznonexistent')
        assert resp.status_code == 200
        assert resp.get_json()['count'] == 0


# --- Tags ---

class TestTags:
    def test_tags_endpoint(self, populated_client):
        resp = populated_client.get('/api/tags')
        assert resp.status_code == 200
        data = resp.get_json()
        # code-review.md has tags: review, quality — returned as {tag: count}
        assert data['review'] == 1
        assert data['quality'] == 1

    def test_tags_empty(self, client):
        resp = client.get('/api/tags')
        assert resp.status_code == 200
        assert resp.get_json() == {}


# --- Download ---

class TestDownload:
    def test_download_returns_file(self, populated_client):
        resp = populated_client.get('/api/prompts/coding/code-review.md/download')
        assert resp.status_code == 200
        assert 'attachment' in resp.headers.get('Content-Disposition', '')
        assert b'Code Review' in resp.data

    def test_download_not_found(self, client):
        resp = client.get('/api/prompts/nope/missing.md/download')
        assert resp.status_code == 404


# --- Import ---

class TestImport:
    def test_import_valid_md(self, client):
        data = {
            'file': (io.BytesIO(b'# Imported Prompt\n\n## Section\n\nContent here\n'), 'test-import.md'),
            'category': 'imported'
        }
        resp = client.post('/api/prompts/import', data=data, content_type='multipart/form-data')
        assert resp.status_code == 201
        assert resp.get_json()['path'] == 'imported/test-import.md'

    def test_import_non_md_rejected(self, client):
        data = {
            'file': (io.BytesIO(b'not markdown'), 'test.txt'),
            'category': 'imported'
        }
        resp = client.post('/api/prompts/import', data=data, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_import_missing_category(self, client):
        data = {
            'file': (io.BytesIO(b'# Prompt\n'), 'test.md'),
            'category': ''
        }
        resp = client.post('/api/prompts/import', data=data, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_import_duplicate(self, client):
        data = {
            'file': (io.BytesIO(b'# Prompt\n'), 'dupe.md'),
            'category': 'testing'
        }
        client.post('/api/prompts/import', data=data, content_type='multipart/form-data')
        data['file'] = (io.BytesIO(b'# Prompt\n'), 'dupe.md')
        resp = client.post('/api/prompts/import', data=data, content_type='multipart/form-data')
        assert resp.status_code == 409

    def test_import_no_file(self, client):
        resp = client.post('/api/prompts/import', data={'category': 'test'}, content_type='multipart/form-data')
        assert resp.status_code == 400


# --- Backup ---

def _make_zip(files):
    """Helper: create an in-memory ZIP from a dict of {arcname: content_bytes}"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    buf.seek(0)
    return buf


class TestBackup:
    def test_backup_empty(self, client):
        resp = client.get('/api/backup')
        assert resp.status_code == 200
        assert 'application/zip' in resp.content_type
        with zipfile.ZipFile(io.BytesIO(resp.data)) as zf:
            assert zf.namelist() == []

    def test_backup_populated(self, populated_client):
        resp = populated_client.get('/api/backup')
        assert resp.status_code == 200
        with zipfile.ZipFile(io.BytesIO(resp.data)) as zf:
            names = zf.namelist()
            assert 'coding/code-review.md' in names
            assert 'writing/blog-post.md' in names
            assert b'Code Review' in zf.read('coding/code-review.md')

    def test_backup_preserves_structure(self, populated_client):
        resp = populated_client.get('/api/backup')
        with zipfile.ZipFile(io.BytesIO(resp.data)) as zf:
            for name in zf.namelist():
                parts = name.split('/')
                assert len(parts) == 2, f'Expected category/file.md, got {name}'
                assert parts[1].endswith('.md')


# --- Restore ---

class TestRestore:
    def test_restore_creates_files(self, client):
        zf = _make_zip({
            'coding/my-prompt.md': '# My Prompt\n\n## Section\n\nContent\n',
            'writing/blog.md': '# Blog\n\n## Intro\n\nHello\n'
        })
        resp = client.post('/api/restore', data={
            'file': (zf, 'backup.zip'), 'mode': 'skip'
        }, content_type='multipart/form-data')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['created']) == 2
        assert 'coding/my-prompt.md' in data['created']

    def test_restore_skip_existing(self, populated_client):
        zf = _make_zip({'coding/code-review.md': '# Overwritten\n'})
        resp = populated_client.post('/api/restore', data={
            'file': (zf, 'backup.zip'), 'mode': 'skip'
        }, content_type='multipart/form-data')
        data = resp.get_json()
        assert len(data['skipped']) == 1
        assert len(data['overwritten']) == 0

    def test_restore_overwrite_existing(self, populated_client):
        zf = _make_zip({'coding/code-review.md': '# Replaced Content\n'})
        resp = populated_client.post('/api/restore', data={
            'file': (zf, 'backup.zip'), 'mode': 'overwrite'
        }, content_type='multipart/form-data')
        data = resp.get_json()
        assert len(data['overwritten']) == 1
        # Verify content was actually replaced
        detail = populated_client.get('/api/prompts/coding/code-review.md')
        assert b'Replaced Content' in detail.data

    def test_restore_rejects_non_zip(self, client):
        resp = client.post('/api/restore', data={
            'file': (io.BytesIO(b'not a zip'), 'backup.txt'), 'mode': 'skip'
        }, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_restore_rejects_traversal(self, client):
        zf = _make_zip({'../../etc/evil.md': 'hacked', '../secret.md': 'stolen'})
        resp = client.post('/api/restore', data={
            'file': (zf, 'backup.zip'), 'mode': 'skip'
        }, content_type='multipart/form-data')
        data = resp.get_json()
        assert len(data['created']) == 0
        assert len(data['errors']) >= 1

    def test_restore_invalid_zip(self, client):
        resp = client.post('/api/restore', data={
            'file': (io.BytesIO(b'garbage data'), 'backup.zip'), 'mode': 'skip'
        }, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_restore_skips_non_md(self, client):
        zf = _make_zip({
            'coding/prompt.md': '# Valid\n',
            'coding/readme.txt': 'not markdown'
        })
        resp = client.post('/api/restore', data={
            'file': (zf, 'backup.zip'), 'mode': 'skip'
        }, content_type='multipart/form-data')
        data = resp.get_json()
        assert len(data['created']) == 1
        assert 'coding/prompt.md' in data['created']

    def test_restore_no_file(self, client):
        resp = client.post('/api/restore', data={'mode': 'skip'}, content_type='multipart/form-data')
        assert resp.status_code == 400
