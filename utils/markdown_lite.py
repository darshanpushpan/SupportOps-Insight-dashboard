"""Minimal Markdown rendering for local documentation pages."""

import html
import posixpath
import re

LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)\s]+)\)')


def _resolve_link(target: str, doc_dir: str) -> str:
    """Resolve a Markdown link target to an href.

    Absolute app routes and external URLs pass through unchanged. Relative
    ``.md`` paths are resolved against the current document's directory and
    rewritten to the ``/knowledge/view`` route.
    """
    if target.startswith(('/', 'http://', 'https://', '#')):
        return target
    if target.endswith('.md'):
        joined = posixpath.normpath(posixpath.join(doc_dir, target))
        return f'/knowledge/view?path={joined}'
    return target


def render_markdown(text: str, doc_dir: str = '') -> str:
    """Convert a subset of Markdown to HTML without extra packages.

    Args:
        text: Raw Markdown source.
        doc_dir: Posix-style directory of the source document, used to
            resolve relative links (e.g. ``docs/runbooks``).
    """
    lines = text.replace('\r\n', '\n').split('\n')
    html_parts = []
    in_list = False
    in_code = False
    code_lines = []
    table_rows = []

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append('</ul>')
            in_list = False

    def close_table():
        nonlocal table_rows
        if not table_rows:
            return
        body = []
        for index, cells in enumerate(table_rows):
            tag = 'th' if index == 0 else 'td'
            row = ''.join(f'<{tag}>{_inline(cell, doc_dir)}</{tag}>' for cell in cells)
            body.append(f'<tr>{row}</tr>')
        html_parts.append('<div class="table-responsive"><table>' + ''.join(body) + '</table></div>')
        table_rows = []

    for line in lines:
        if line.strip().startswith('```'):
            close_table()
            if in_code:
                html_parts.append('<pre><code>' + html.escape('\n'.join(code_lines)) + '</code></pre>')
                code_lines = []
                in_code = False
            else:
                close_list()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue

        if line.strip().startswith('|') and '|' in line.strip()[1:]:
            close_list()
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if all(cell and set(cell) <= set('-: ') for cell in cells):
                continue
            table_rows.append(cells)
            continue

        close_table()

        if not line.strip():
            close_list()
            continue

        heading = re.match(r'^(#{1,4})\s+(.*)$', line)
        if heading:
            close_list()
            level = len(heading.group(1))
            html_parts.append(f'<h{level}>{_inline(heading.group(2), doc_dir)}</h{level}>')
            continue

        if re.match(r'^[-*]\s+', line.strip()):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            item = re.sub(r'^[-*]\s+', '', line.strip())
            html_parts.append(f'<li>{_inline(item, doc_dir)}</li>')
            continue

        close_list()
        html_parts.append(f'<p>{_inline(line, doc_dir)}</p>')

    close_list()
    close_table()
    if in_code:
        html_parts.append('<pre><code>' + html.escape('\n'.join(code_lines)) + '</code></pre>')
    return '\n'.join(html_parts)


def _inline(text: str, doc_dir: str = '') -> str:
    escaped = html.escape(text)
    escaped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
    escaped = re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)
    escaped = LINK_PATTERN.sub(
        lambda m: f'<a href="{_resolve_link(m.group(2), doc_dir)}">{m.group(1)}</a>',
        escaped,
    )
    return escaped
