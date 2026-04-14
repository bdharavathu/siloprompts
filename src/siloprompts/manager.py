"""
PromptManager — core business logic for managing prompt files
"""

import os
import re
import io
import zipfile
from pathlib import Path
from datetime import datetime
import markdown


class PromptManager:
    """Manages prompt files and operations"""

    def __init__(self, prompts_path: Path):
        self.prompts_path = Path(prompts_path)

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
        safe_query = re.escape(query)

        for md_file in self.prompts_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if re.search(safe_query, content, flags):
                    relative_path = md_file.relative_to(self.prompts_path)
                    category = relative_path.parts[0] if len(relative_path.parts) > 1 else 'root'

                    # Find matching lines
                    lines = content.split('\n')
                    matches = []
                    for line_num, line in enumerate(lines):
                        if re.search(safe_query, line, flags):
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
                        'match_count': len(re.findall(safe_query, content, flags))
                    })
            except Exception as e:
                print(f"Error searching {md_file}: {e}")

        return results

    def backup_zip(self):
        """Create a ZIP archive of all prompts preserving category/filename structure"""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for md_file in sorted(self.prompts_path.rglob('*.md')):
                # Skip hidden directories
                if any(part.startswith('.') for part in md_file.relative_to(self.prompts_path).parts):
                    continue
                relative = md_file.relative_to(self.prompts_path)
                zf.write(md_file, arcname=str(relative))
        buffer.seek(0)
        return buffer

    def restore_from_zip(self, zip_buffer, mode='skip'):
        """Restore prompts from a ZIP archive

        Args:
            zip_buffer: file-like object containing ZIP data
            mode: 'skip' to skip existing files, 'overwrite' to replace them

        Returns:
            dict with created, skipped, overwritten, and errors lists
        """
        results = {'created': [], 'skipped': [], 'overwritten': [], 'errors': []}

        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            entries = [e for e in zf.infolist() if not e.is_dir()]
            if len(entries) > 500:
                raise ValueError('ZIP contains too many files (max 500)')

            for entry in entries:
                name = entry.filename

                # Skip non-.md files
                if not name.endswith('.md'):
                    continue

                # Security: normalize and validate path
                normalized = os.path.normpath(name)
                if normalized.startswith('..') or normalized.startswith('/'):
                    results['errors'].append(f'Invalid path: {name}')
                    continue

                parts = Path(normalized).parts
                # Require exactly category/filename.md structure
                if len(parts) != 2:
                    results['errors'].append(f'Invalid structure (need category/file.md): {name}')
                    continue

                category, filename = parts
                stem = os.path.splitext(filename)[0]

                # Sanitize category and filename
                safe_category = re.sub(r'[^a-zA-Z0-9_-]', '-', category).strip('-')
                safe_stem = re.sub(r'[^a-zA-Z0-9_-]', '-', stem).strip('-')
                if not safe_category or not safe_stem:
                    results['errors'].append(f'Invalid name after sanitization: {name}')
                    continue

                # Check per-file size (1MB)
                if entry.file_size > 1_000_000:
                    results['errors'].append(f'File too large (max 1MB): {name}')
                    continue

                target = self.prompts_path / safe_category / f'{safe_stem}.md'

                if target.exists():
                    if mode == 'skip':
                        results['skipped'].append(f'{safe_category}/{safe_stem}.md')
                        continue
                    else:
                        results['overwritten'].append(f'{safe_category}/{safe_stem}.md')
                else:
                    results['created'].append(f'{safe_category}/{safe_stem}.md')

                target.parent.mkdir(parents=False, exist_ok=True)
                target.write_bytes(zf.read(entry))

        return results
