"""
SiloPrompts Web Application
Flask app factory and API routes
"""

import os
import io
import re
import shutil
import zipfile
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory, send_file, current_app
from datetime import datetime

from siloprompts.manager import PromptManager


DEFAULT_PROMPTS_DIR = os.path.expanduser('~/.siloprompts/prompts')
DEFAULT_DATA_DIR = os.path.expanduser('~/.siloprompts/data')


def create_app(prompts_dir=None, data_dir=None):
    """Create and configure the Flask application.

    Path resolution order:
    1. Explicit argument (CLI --prompts / --data)
    2. Environment variable (PROMPTS_DIR / DATA_DIR) — used by Docker/K8s
    3. Default (~/.siloprompts/prompts / ~/.siloprompts/data) — used by pip install
    """
    prompts_path = Path(prompts_dir or os.environ.get('PROMPTS_DIR', DEFAULT_PROMPTS_DIR))
    data_path = Path(data_dir or os.environ.get('DATA_DIR', DEFAULT_DATA_DIR))

    prompts_path.mkdir(parents=True, exist_ok=True)
    data_path.mkdir(parents=True, exist_ok=True)

    # First run: copy bundled starter prompts if directory is empty
    # The .initialized marker prevents re-copying after user deletes all prompts
    initialized_marker = prompts_path / '.initialized'
    if not initialized_marker.exists() and not any(prompts_path.glob('*/*.md')):
        bundled = Path(__file__).parent / 'default_prompts'
        if bundled.is_dir():
            for src_file in bundled.glob('*/*.md'):
                dest = prompts_path / src_file.relative_to(bundled)
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    shutil.copy2(src_file, dest)
        initialized_marker.touch()

    flask_app = Flask(__name__, template_folder='templates')
    flask_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

    flask_app.prompt_manager = PromptManager(prompts_path)
    flask_app.data_dir = data_path
    flask_app.prompts_dir = prompts_path

    _register_routes(flask_app)

    return flask_app


def _register_routes(flask_app):
    """Register all API routes on the Flask app"""

    @flask_app.route('/')
    def index():
        """Main page"""
        from siloprompts import __version__
        return render_template('index.html', version=__version__)

    @flask_app.route('/api/categories')
    def api_categories():
        """Get all categories"""
        categories = current_app.prompt_manager.get_categories()
        return jsonify(categories)

    @flask_app.route('/api/prompts')
    def api_prompts():
        """Get all prompts"""
        prompts = current_app.prompt_manager.get_all_prompts()
        return jsonify(prompts)

    @flask_app.route('/api/prompts/<path:prompt_path>')
    def api_prompt_detail(prompt_path):
        """Get detailed prompt content"""
        content = current_app.prompt_manager.get_prompt_content(prompt_path)

        if content is None:
            return jsonify({'error': 'Prompt not found'}), 404

        return jsonify(content)

    @flask_app.route('/api/tags')
    def api_tags():
        """Get all unique tags with counts"""
        prompts = current_app.prompt_manager.get_all_prompts()
        tag_counts = {}
        for prompt in prompts:
            for tag in prompt.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return jsonify(tag_counts)

    @flask_app.route('/api/search')
    def api_search():
        """Search prompts"""
        query = request.args.get('q', '')
        case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'

        if not query:
            return jsonify({'error': 'Query parameter required'}), 400

        results = current_app.prompt_manager.search_prompts(query, case_sensitive)
        return jsonify({
            'query': query,
            'count': len(results),
            'results': results
        })

    @flask_app.route('/api/prompts', methods=['POST'])
    def api_create_prompt():
        """Create a new prompt"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400

        for field in ('category', 'filename', 'title', 'sections'):
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if request.content_length and request.content_length > 1_000_000:
            return jsonify({'error': 'Request too large (max 1MB)'}), 413

        tags = data.get('tags')

        try:
            path = current_app.prompt_manager.create_prompt(
                data['category'], data['filename'], data['title'], data['sections'], tags=tags
            )
            return jsonify({'path': path, 'message': 'Prompt created successfully'}), 201
        except FileExistsError:
            return jsonify({'error': 'Prompt already exists'}), 409
        except ValueError:
            return jsonify({'error': 'Invalid prompt data'}), 400

    @flask_app.route('/api/prompts/<path:prompt_path>', methods=['PUT'])
    def api_update_prompt(prompt_path):
        """Update an existing prompt"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400

        for field in ('title', 'sections'):
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if request.content_length and request.content_length > 1_000_000:
            return jsonify({'error': 'Request too large (max 1MB)'}), 413

        tags = data.get('tags')

        try:
            path = current_app.prompt_manager.update_prompt(prompt_path, data['title'], data['sections'], tags=tags)
            return jsonify({'path': path, 'message': 'Prompt updated successfully'})
        except FileNotFoundError:
            return jsonify({'error': 'Prompt not found'}), 404
        except ValueError:
            return jsonify({'error': 'Invalid prompt data'}), 400

    @flask_app.route('/api/prompts/<path:prompt_path>', methods=['DELETE'])
    def api_delete_prompt(prompt_path):
        """Delete a prompt"""
        delete_empty = request.args.get('delete_empty_category', 'false').lower() == 'true'

        try:
            result = current_app.prompt_manager.delete_prompt(prompt_path, delete_empty)
            return jsonify({'message': 'Prompt deleted successfully', **result})
        except FileNotFoundError:
            return jsonify({'error': 'Prompt not found'}), 404
        except ValueError:
            return jsonify({'error': 'Invalid path'}), 400

    @flask_app.route('/api/prompts/<path:prompt_path>/download')
    def api_download_prompt(prompt_path):
        """Download a prompt as .md file"""
        try:
            file_path = current_app.prompt_manager._validate_path(prompt_path)
        except (ValueError, RuntimeError):
            return jsonify({'error': 'Invalid path'}), 400

        if not file_path.exists() or not file_path.is_file():
            return jsonify({'error': 'Prompt not found'}), 404

        return send_file(file_path, as_attachment=True, download_name=file_path.name)

    @flask_app.route('/api/prompts/import', methods=['POST'])
    def api_import_prompt():
        """Import a .md prompt file"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        category = request.form.get('category', '').strip()

        if not file.filename or not file.filename.endswith('.md'):
            return jsonify({'error': 'Only .md files are allowed'}), 400

        if not category:
            return jsonify({'error': 'Category is required'}), 400

        try:
            current_app.prompt_manager._validate_filename(category)
        except ValueError:
            return jsonify({'error': 'Invalid category name'}), 400

        # Read and validate size
        content = file.read()
        if len(content) > 1_000_000:
            return jsonify({'error': 'File too large (max 1MB)'}), 413

        # Sanitize filename
        raw_name = os.path.splitext(file.filename)[0]
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '-', raw_name).strip('-')
        if not safe_name:
            return jsonify({'error': 'Invalid filename'}), 400

        relative_path = f"{category}/{safe_name}.md"
        try:
            file_path = current_app.prompt_manager._validate_path(relative_path)
        except (ValueError, RuntimeError):
            return jsonify({'error': 'Invalid path'}), 400

        if file_path.exists():
            return jsonify({'error': f'File already exists: {relative_path}'}), 409

        file_path.parent.mkdir(parents=False, exist_ok=True)
        file_path.write_bytes(content)

        return jsonify({'path': relative_path, 'message': 'Prompt imported successfully'}), 201

    @flask_app.route('/api/backup')
    def api_backup():
        """Download all prompts as a ZIP backup"""
        buffer = current_app.prompt_manager.backup_zip()
        timestamp = datetime.now().strftime('%Y-%m-%dT%H%M%S')
        return send_file(
            buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'siloprompts-backup-{timestamp}.zip'
        )

    @flask_app.route('/api/restore', methods=['POST'])
    def api_restore():
        """Restore prompts from a ZIP backup"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename or not file.filename.endswith('.zip'):
            return jsonify({'error': 'Only .zip files are allowed'}), 400

        if request.content_length and request.content_length > 10_000_000:
            return jsonify({'error': 'File too large (max 10MB)'}), 413

        mode = request.form.get('mode', 'skip')
        if mode not in ('skip', 'overwrite'):
            return jsonify({'error': 'Invalid mode. Use "skip" or "overwrite".'}), 400

        zip_bytes = file.read()
        if len(zip_bytes) > 10_000_000:
            return jsonify({'error': 'File too large (max 10MB)'}), 413

        try:
            results = current_app.prompt_manager.restore_from_zip(io.BytesIO(zip_bytes), mode)
        except zipfile.BadZipFile:
            return jsonify({'error': 'Invalid ZIP file'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid restore data'}), 400

        total = len(results['created']) + len(results['overwritten'])
        return jsonify({
            'message': f'Restored {total} prompt(s)',
            **results
        })

    @flask_app.route('/health')
    def health():
        """Health check endpoint for Kubernetes"""
        from siloprompts import __version__
        return jsonify({
            'status': 'healthy',
            'version': __version__,
            'prompts_dir': str(current_app.prompts_dir),
            'prompts_exists': current_app.prompts_dir.exists(),
            'timestamp': datetime.now().isoformat()
        })

    @flask_app.route('/favicon.ico')
    def favicon():
        """Serve favicon"""
        return send_from_directory(
            os.path.join(flask_app.static_folder, 'images'),
            'siloprompts-logo.svg',
            mimetype='image/svg+xml'
        )


# Module-level app for gunicorn: `gunicorn siloprompts.web:app`
app = create_app()
