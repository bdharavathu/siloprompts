#!/usr/bin/env python3
"""
SiloPrompts CLI - Command-line tool for managing and searching prompts
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import List, Tuple


class SiloPrompts:
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.prompts_dir = self.base_dir / "prompts"

    def search(self, keyword: str, case_sensitive: bool = False) -> List[Tuple[str, str, List[str]]]:
        """Search for prompts containing the keyword"""
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE

        for md_file in self.prompts_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if re.search(keyword, content, flags):
                    # Extract matching lines with context
                    lines = content.split('\n')
                    matching_lines = [
                        line for line in lines
                        if re.search(keyword, line, flags)
                    ]

                    relative_path = md_file.relative_to(self.prompts_dir)
                    results.append((str(relative_path), str(md_file), matching_lines[:3]))
            except Exception as e:
                print(f"Error reading {md_file}: {e}", file=sys.stderr)

        return results

    def list_prompts(self) -> dict:
        """List all available prompts organized by category"""
        categories = {}

        for md_file in self.prompts_dir.rglob("*.md"):
            relative_path = md_file.relative_to(self.prompts_dir)
            category = relative_path.parts[0] if len(relative_path.parts) > 1 else "root"

            if category not in categories:
                categories[category] = []
            categories[category].append(relative_path)

        return categories

    def show_prompt(self, file_path: str) -> str:
        """Display the contents of a specific prompt file"""
        full_path = self.prompts_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_prompt_sections(self, file_path: str) -> List[Tuple[str, str]]:
        """Extract individual prompt sections from a file"""
        content = self.show_prompt(file_path)
        sections = []

        # Split by ## headers
        parts = re.split(r'^## ', content, flags=re.MULTILINE)

        for part in parts[1:]:  # Skip first part (file header)
            lines = part.split('\n', 1)
            title = lines[0].strip()
            body = lines[1] if len(lines) > 1 else ""
            sections.append((title, body))

        return sections

    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard (requires pyperclip)"""
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except ImportError:
            print("Error: pyperclip not installed. Install with: pip install pyperclip")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='SiloPrompts CLI - Manage your AI prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "debug"              # Search for prompts containing "debug"
  %(prog)s list                        # List all prompt categories
  %(prog)s show coding/code-review.md  # Display a specific prompt file
  %(prog)s sections coding/debugging.md # List all prompts in a file
  %(prog)s copy coding/debugging.md 0  # Copy first prompt to clipboard
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for prompts')
    search_parser.add_argument('keyword', help='Keyword to search for')
    search_parser.add_argument('-c', '--case-sensitive', action='store_true',
                              help='Case-sensitive search')

    # List command
    list_parser = subparsers.add_parser('list', help='List all prompts')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show a specific prompt file')
    show_parser.add_argument('file', help='Path to prompt file (e.g., coding/code-review.md)')

    # Sections command
    sections_parser = subparsers.add_parser('sections', help='List prompt sections in a file')
    sections_parser.add_argument('file', help='Path to prompt file')

    # Copy command
    copy_parser = subparsers.add_parser('copy', help='Copy a prompt to clipboard')
    copy_parser.add_argument('file', help='Path to prompt file')
    copy_parser.add_argument('section', type=int, help='Section number (0-based)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    db = SiloPrompts()

    try:
        if args.command == 'search':
            results = db.search(args.keyword, args.case_sensitive)

            if not results:
                print(f"No prompts found matching '{args.keyword}'")
                return

            print(f"\nFound {len(results)} file(s) matching '{args.keyword}':\n")
            for rel_path, full_path, matches in results:
                print(f"📄 {rel_path}")
                print(f"   {full_path}")
                for match in matches:
                    print(f"   → {match.strip()[:80]}...")
                print()

        elif args.command == 'list':
            categories = db.list_prompts()

            print("\n📚 Available Prompts:\n")
            for category, files in sorted(categories.items()):
                print(f"📁 {category}/")
                for file in sorted(files):
                    print(f"   └─ {file.name}")
                print()

        elif args.command == 'show':
            content = db.show_prompt(args.file)
            print(content)

        elif args.command == 'sections':
            sections = db.extract_prompt_sections(args.file)

            print(f"\n📋 Prompts in {args.file}:\n")
            for idx, (title, _) in enumerate(sections):
                print(f"[{idx}] {title}")
            print(f"\nUse 'prompt-cli.py copy {args.file} <number>' to copy a prompt")

        elif args.command == 'copy':
            sections = db.extract_prompt_sections(args.file)

            if args.section < 0 or args.section >= len(sections):
                print(f"Error: Section {args.section} not found. Available: 0-{len(sections)-1}")
                return

            title, content = sections[args.section]

            # Extract just the prompt text (inside code blocks)
            code_blocks = re.findall(r'```\n(.*?)```', content, re.DOTALL)
            prompt_text = code_blocks[0] if code_blocks else content

            if db.copy_to_clipboard(prompt_text):
                print(f"✅ Copied '{title}' to clipboard!")
            else:
                print("\n" + "="*60)
                print(prompt_text)
                print("="*60)
                print("\nCopy the text above manually (pyperclip not available)")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
