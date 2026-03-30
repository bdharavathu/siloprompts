#!/usr/bin/env python3
"""
SiloPrompts Web Application
A web interface for browsing and managing AI prompts
"""

import os
import re
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
import markdown
from datetime import datetime

app = Flask(__name__, template_folder='html_templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

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

                prompts.append({
                    'id': str(relative_path),
                    'title': title,
                    'category': category,
                    'filename': md_file.name,
                    'path': str(relative_path),
                    'sections': len(prompt_sections),
                    'size': md_file.stat().st_size,
                    'modified': datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                })
            except Exception as e:
                print(f"Error processing {md_file}: {e}")

        return prompts

    def get_prompt_content(self, prompt_path: str):
        """Get full content of a prompt file"""
        file_path = self.prompts_path / prompt_path

        # Security: Prevent path traversal attacks
        try:
            file_path = file_path.resolve()
            file_path.relative_to(self.prompts_path.resolve())
        except (ValueError, RuntimeError):
            # Path is outside prompts directory
            return None

        if not file_path.exists() or not file_path.is_file():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse into sections
        sections = self._parse_sections(content)

        # Convert markdown to HTML for preview
        html_content = markdown.markdown(content, extensions=['fenced_code', 'codehilite'])

        return {
            'path': prompt_path,
            'raw': content,
            'html': html_content,
            'sections': sections
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
    return render_template('index.html')


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


@app.route('/health')
def health():
    """Health check endpoint for Kubernetes"""
    return jsonify({
        'status': 'healthy',
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
