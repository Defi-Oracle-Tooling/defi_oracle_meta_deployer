import markdown
import os
from flask import Markup

class MarkdownConverter:
    def __init__(self, docs_dir='docs'):
        self.docs_dir = docs_dir
        self.md = markdown.Markdown(extensions=[
            'fenced_code',
            'codehilite',
            'tables',
            'toc',
            'mdx_math',
            'markdown_include.include'
        ])
    
    def convert_file(self, filename):
        """Convert a markdown file to HTML"""
        try:
            file_path = os.path.join(self.docs_dir, f'{filename}.md')
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.convert_text(content)
        except FileNotFoundError:
            return None
    
    def convert_text(self, text):
        """Convert markdown text to HTML"""
        self.md.reset()  # Reset markdown parser state
        html = self.md.convert(text)
        return Markup(html)  # Mark as safe for Jinja2
    
    def get_toc(self):
        """Get table of contents from last conversion"""
        if hasattr(self.md, 'toc'):
            return Markup(self.md.toc)
        return ''