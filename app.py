#!/usr/bin/env python3
"""
SiloPrompts Web Application
A web interface for browsing and managing AI prompts
"""

import os
import re
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
import markdown
from datetime import datetime

app = Flask(__name__, template_folder='html_templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

VERSION = '1.0.2'

# Paths - can be overridden by environment variables
PROMPTS_DIR = Path(os.environ.get('PROMPTS_DIR', '/app/prompts'))
DATA_DIR = Path(os.environ.get('DATA_DIR', '/app/data'))


class PromptManager:
    """Manages prompt files and operations"""

    def __init__(self, prompts_path: Path):
        self.prompts_path = prompts_path

    def get_categories(self):
        """Get all prompt categories"""
        categories = {}
        for category_dir in self.prompts_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                prompt_files = list(category_dir.glob('*.md'))
                categories[category_dir.name] = {
                    'name': category_dir.name,
                    'count': len(prompt_files),
                    'files': [f.name for f in prompt_files]
                }
        return categories

    def get_all_prompts(self):
        """Get all prompts with metadata"""
        prompts = []
        for md_file in self.prompts_path.rglob('*.md'):
            try:
                relative_path = md_file.relative_to(self.prompts_path)
                category = relative_path.parts[0] if len(relative_path.parts) > 1 else 'root'

                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract title from first # header
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else md_file.stem

                # Count prompts (## headers)
                prompt_sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)

                # Extract tags
                tags = self._extract_tags(content)

                prompts.append({
                    'id': str(relative_path),
                    'title': title,
                    'category': category,
                    'filename': md_file.name,
                    'path': str(relative_path),
                    'sections': len(prompt_sections),
                    'size': md_file.stat().st_size,
                    'modified': datetime.fromtimestamp(md_file.stat().st_mtime).isoformat(),
                    'tags': tags
                })
            except Exception as e:
                print(f"Error processing {md_file}: {e}")

        return prompts

    def _validate_path(self, prompt_path: str):
        """Validate and resolve a prompt path, preventing traversal attacks"""
        file_path = (self.prompts_path / prompt_path).resolve()
        file_path.relative_to(self.prompts_path.resolve())
        return file_path

    @staticmethod
    def _validate_filename(name: str):
        """Validate that a name contains only safe characters"""
        if not name or not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError(f"Invalid name: '{name}'. Only letters, numbers, hyphens and underscores allowed.")
        return name

    @staticmethod
    def _extract_tags(content: str):
        """Extract tags from Tags: line in header"""
        match = re.search(r'^Tags:\s*(.+)$', content, re.MULTILINE)
        if not match:
            return []
        return [tag.strip().lower() for tag in match.group(1).split(',') if tag.strip()]

    @staticmethod
    def _extract_description(content: str):
        """Extract description text between # title and first ## section, skipping Tags: line"""
        parts = re.split(r'^## ', content, maxsplit=1, flags=re.MULTILINE)
        if len(parts) < 2:
            return ''
        header = parts[0]
        lines = header.split('\n')
        desc_lines = []
        past_title = False
        for line in lines:
            if not past_title:
                if re.match(r'^#\s+', line):
                    past_title = True
                continue
            stripped = line.strip()
            if stripped and not re.match(r'^Tags:\s*', stripped):
                desc_lines.append(stripped)
        return '\n'.join(desc_lines)

    @staticmethod
    def _sections_to_markdown(title: str, sections: list, description: str = '', tags: list = None):
        """Convert title and sections list back to markdown format"""
        lines = [f"# {title}", ""]
        if tags:
            lines.append(f"Tags: {', '.join(tags)}")
            lines.append("")
        if description:
            lines.append(description)
            lines.append("")
        for section in sections:
            lines.append(f"## {section['title']}")
            lines.append("")
            lines.append("```")
            lines.append(section['prompt'])
            lines.append("```")
            lines.append("")
        return "\n".join(lines)

    def create_prompt(self, category: str, filename: str, title: str, sections: list, tags: list = None):
        """Create a new prompt file"""
        self._validate_filename(category)
        self._validate_filename(filename)

        relative_path = f"{category}/{filename}.md"
        file_path = self._validate_path(relative_path)

        if file_path.exists():
            raise FileExistsError(f"Prompt already exists: {relative_path}")

        file_path.parent.mkdir(parents=False, exist_ok=True)
        content = self._sections_to_markdown(title, sections, tags=tags)
        file_path.write_text(content, encoding='utf-8')
        return relative_path

    def update_prompt(self, prompt_path: str, title: str, sections: list, tags: list = None):
        """Update an existing prompt file"""
        file_path = self._validate_path(prompt_path)

        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")

        existing_content = file_path.read_text(encoding='utf-8')
        description = self._extract_description(existing_content)

        # Preserve existing tags if not provided
        if tags is None:
            tags = self._extract_tags(existing_content)

        content = self._sections_to_markdown(title, sections, description, tags)
        file_path.write_text(content, encoding='utf-8')
        return prompt_path

    def delete_prompt(self, prompt_path: str, delete_empty_category: bool = False):
        """Delete a prompt file"""
        file_path = self._validate_path(prompt_path)

        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")

        file_path.unlink()
        category_deleted = False

        if delete_empty_category:
            parent = file_path.parent
            if parent != self.prompts_path.resolve() and not any(parent.glob('*.md')):
                parent.rmdir()
                category_deleted = True

        return {'category_deleted': category_deleted}

    def get_prompt_content(self, prompt_path: str):
        """Get full content of a prompt file"""
        try:
            file_path = self._validate_path(prompt_path)
        except (ValueError, RuntimeError):
            return None

        if not file_path.exists() or not file_path.is_file():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse into sections
        sections = self._parse_sections(content)

        # Convert markdown to HTML for preview
        html_content = markdown.markdown(content, extensions=['fenced_code', 'codehilite'])

        # Extract description and tags
        description = self._extract_description(content)
        tags = self._extract_tags(content)

        return {
            'path': prompt_path,
            'raw': content,
            'html': html_content,
            'sections': sections,
            'description': description,
            'tags': tags
        }

    def _parse_sections(self, content: str):
        """Parse markdown content into sections"""
        sections = []

        # Split by ## headers
        parts = re.split(r'^## ', content, flags=re.MULTILINE)

        for i, part in enumerate(parts[1:]):  # Skip first part (file header)
            lines = part.split('\n', 1)
            title = lines[0].strip()
            body = lines[1] if len(lines) > 1 else ""

            # Extract code blocks (prompts are usually in code blocks)
            code_blocks = re.findall(r'```\n(.*?)```', body, re.DOTALL)
            prompt_text = code_blocks[0] if code_blocks else body

            sections.append({
                'id': i,
                'title': title,
                'content': body,
                'prompt': prompt_text.strip(),
                'has_code_block': len(code_blocks) > 0
            })

        return sections

    def search_prompts(self, query: str, case_sensitive: bool = False):
        """Search prompts by keyword"""
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE

        for md_file in self.prompts_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if re.search(query, content, flags):
                    relative_path = md_file.relative_to(self.prompts_path)
                    category = relative_path.parts[0] if len(relative_path.parts) > 1 else 'root'

                    # Find matching lines
                    lines = content.split('\n')
                    matches = []
                    for line_num, line in enumerate(lines):
                        if re.search(query, line, flags):
                            matches.append({
                                'line': line_num + 1,
                                'text': line.strip()[:150]  # Truncate long lines
                            })
                            if len(matches) >= 5:  # Limit matches per file
                                break

                    results.append({
                        'path': str(relative_path),
                        'category': category,
                        'filename': md_file.name,
                        'matches': matches,
                        'match_count': len(re.findall(query, content, flags))
                    })
            except Exception as e:
                print(f"Error searching {md_file}: {e}")

        return results


# Initialize prompt manager
prompt_manager = PromptManager(PROMPTS_DIR)


# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', version=VERSION)


@app.route('/api/categories')
def api_categories():
    """Get all categories"""
    categories = prompt_manager.get_categories()
    return jsonify(categories)


@app.route('/api/prompts')
def api_prompts():
    """Get all prompts"""
    prompts = prompt_manager.get_all_prompts()
    return jsonify(prompts)


@app.route('/api/prompts/<path:prompt_path>')
def api_prompt_detail(prompt_path):
    """Get detailed prompt content"""
    content = prompt_manager.get_prompt_content(prompt_path)

    if content is None:
        return jsonify({'error': 'Prompt not found'}), 404

    return jsonify(content)


@app.route('/api/tags')
def api_tags():
    """Get all unique tags with counts"""
    prompts = prompt_manager.get_all_prompts()
    tag_counts = {}
    for prompt in prompts:
        for tag in prompt.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    return jsonify(tag_counts)


@app.route('/api/search')
def api_search():
    """Search prompts"""
    query = request.args.get('q', '')
    case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'

    if not query:
        return jsonify({'error': 'Query parameter required'}), 400

    results = prompt_manager.search_prompts(query, case_sensitive)
    return jsonify({
        'query': query,
        'count': len(results),
        'results': results
    })


@app.route('/api/prompts', methods=['POST'])
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
        path = prompt_manager.create_prompt(
            data['category'], data['filename'], data['title'], data['sections'], tags=tags
        )
        return jsonify({'path': path, 'message': 'Prompt created successfully'}), 201
    except FileExistsError as e:
        return jsonify({'error': str(e)}), 409
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/prompts/<path:prompt_path>', methods=['PUT'])
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
        path = prompt_manager.update_prompt(prompt_path, data['title'], data['sections'], tags=tags)
        return jsonify({'path': path, 'message': 'Prompt updated successfully'})
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/prompts/<path:prompt_path>', methods=['DELETE'])
def api_delete_prompt(prompt_path):
    """Delete a prompt"""
    delete_empty = request.args.get('delete_empty_category', 'false').lower() == 'true'

    try:
        result = prompt_manager.delete_prompt(prompt_path, delete_empty)
        return jsonify({'message': 'Prompt deleted successfully', **result})
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/prompts/<path:prompt_path>/download')
def api_download_prompt(prompt_path):
    """Download a prompt as .md file"""
    try:
        file_path = prompt_manager._validate_path(prompt_path)
    except (ValueError, RuntimeError):
        return jsonify({'error': 'Invalid path'}), 400

    if not file_path.exists() or not file_path.is_file():
        return jsonify({'error': 'Prompt not found'}), 404

    return send_file(file_path, as_attachment=True, download_name=file_path.name)


@app.route('/api/prompts/import', methods=['POST'])
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
        prompt_manager._validate_filename(category)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

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
        file_path = prompt_manager._validate_path(relative_path)
    except (ValueError, RuntimeError):
        return jsonify({'error': 'Invalid path'}), 400

    if file_path.exists():
        return jsonify({'error': f'File already exists: {relative_path}'}), 409

    file_path.parent.mkdir(parents=False, exist_ok=True)
    file_path.write_bytes(content)

    return jsonify({'path': relative_path, 'message': 'Prompt imported successfully'}), 201


@app.route('/health')
def health():
    """Health check endpoint for Kubernetes"""
    return jsonify({
        'status': 'healthy',
        'version': VERSION,
        'prompts_dir': str(PROMPTS_DIR),
        'prompts_exists': PROMPTS_DIR.exists(),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory(
        os.path.join(app.static_folder, 'images'),
        'siloprompts-logo.svg',
        mimetype='image/svg+xml'
    )


if __name__ == '__main__':
    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'

    print(f"Starting SiloPrompts Web Interface on port {port}")
    print(f"Prompts directory: {PROMPTS_DIR}")
    print(f"Data directory: {DATA_DIR}")

    app.run(host='0.0.0.0', port=port, debug=debug)
