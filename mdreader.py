#!/usr/bin/env python3
"""Markdown Reader - renders .md files in Firefox as a desktop app."""

import sys, os, re, subprocess, threading, http.server, socketserver, time
from html import escape as h

def inline_md(text):
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
    return text

def md_to_html(text):
    lines = text.split('\n')
    out, in_list, in_code, code_lang, in_table, table_rows, in_quote = [], False, False, '', False, [], False

    def close_list():
        nonlocal in_list
        if in_list: out.append('</ul>'); in_list = False

    def close_table():
        nonlocal in_table, table_rows
        if in_table and table_rows:
            out.append('<table>')
            for i, row in enumerate(table_rows):
                tag = 'th' if i == 0 else 'td'
                out.append('<tr>' + ''.join(f'<{tag}>{h(c.strip())}</{tag}>' for c in row) + '</tr>')
            out.append('</table>')
        in_table, table_rows = False, []

    def open_table():
        nonlocal in_table, table_rows
        if not in_table:
            in_table = True
            table_rows = []

    def close_quote():
        nonlocal in_quote
        if in_quote: out.append('</blockquote>'); in_quote = False

    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'^`{3,}', line.strip()) or re.match(r'^~{3,}', line.strip()):
            close_list(); close_table(); close_quote()
            if not in_code:
                in_code = True; code_lang = re.sub(r'^[`~]{3,}', '', line.strip()).strip() or ''
                cls = f' class="language-{code_lang}"' if code_lang else ''
                out.append(f'<pre><code{cls}>')
            else: out.append('</code></pre>'); in_code = False
            i += 1; continue
        if in_code: out.append(h(line)); i += 1; continue
        if not line.strip(): close_list(); close_table(); close_quote(); i += 1; continue
        if re.match(r'^(-{3,}|_{3,}|\*{3,})\s*$', line): close_list(); close_table(); close_quote(); out.append('<hr>'); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m: close_list(); close_table(); close_quote(); out.append(f'<h{len(m.group(1))}>{inline_md(m.group(2))}</h{len(m.group(1))}>'); i += 1; continue
        if line.strip().startswith('>'):
            close_list(); close_table()
            if not in_quote: in_quote = True; out.append('<blockquote>')
            out.append(inline_md(re.sub(r'^>\s?', '', line.strip()))); i += 1; continue
        if '|' in line and line.strip().startswith('|'):
            close_list(); close_quote()
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells and not re.match(r'^[\s\-:|]+$', line):
                open_table()
                table_rows.append(cells)
                i += 1
                while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                    c2 = [c.strip() for c in lines[i].split('|')[1:-1]]
                    if re.match(r'^[\s\-:|]+$', lines[i]): i += 1; continue
                    if c2: table_rows.append(c2)
                    i += 1
                close_table(); continue
        m = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if m:
            close_table(); close_quote()
            if not in_list: out.append('<ul>'); in_list = True
            out.append(f'<li>{inline_md(m.group(2))}</li>'); i += 1; continue
        close_list(); close_table(); close_quote()
        if line.strip(): out.append(f'<p>{inline_md(line)}</p>')
        i += 1

    if in_code: out.append('</code></pre>')
    close_list(); close_table(); close_quote()
    return '\n'.join(out)

def render(path):
    with open(path, 'r', encoding='utf-8') as f: raw = f.read()
    body = md_to_html(raw)
    title = h(os.path.basename(path))
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
body {{ max-width: 860px; margin: 0 auto; padding: 2rem 2.5rem; line-height: 1.7; color: #333; font-family: system-ui, -apple-system, sans-serif; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #f5f5f5; font-weight: 600; }}
code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace, sans-serif; font-size: 0.9em; color: #d63384; }}
pre {{ background: #f4f4f4; padding: 16px; border-radius: 6px; overflow-x: auto; margin: 1rem 0; }}
pre code {{ background: none; padding: 0; color: #333; }}
h1, h2 {{ border-bottom: 1px solid #eee; padding-bottom: 8px; margin-top: 1.5rem; color: #1a1a2e; }}
blockquote {{ border-left: 3px solid #89b4fa; padding-left: 16px; color: #555; margin: 1rem 0; }}
a {{ color: #2563eb; }} img {{ max-width: 100%; }} hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0; }}
ul {{ padding-left: 1.5rem; }}
</style></head><body>{body}</body></html>'''

def main():
    if len(sys.argv) < 2: print("Usage: python3 mdreader.py <file.md>"); sys.exit(1)
    path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(path): print(f"File not found: {path}"); sys.exit(1)

    html = render(path)
    out_dir = os.path.expanduser('~/.cache/mdreader')
    os.makedirs(out_dir, exist_ok=True)

    # Unique filename based on mtime + size so file changes always show up fresh
    stat = os.stat(path)
    fname = f'{os.path.basename(path)}_{int(stat.st_mtime)}_{stat.st_size}.html'
    with open(os.path.join(out_dir, fname), 'w') as f: f.write(html)

    PORT = 18765
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k): super().__init__(*a, directory=out_dir, **k)

    server = socketserver.TCPServer(('', PORT), Handler)
    serve_thread = threading.Thread(target=server.serve_forever, daemon=True)
    serve_thread.start()

    url = f'http://localhost:{PORT}/{fname}'
    print(f"Opening: {url}")
    sys.stdout.flush()

    # Wait for server to be ready (try a few times in case port is still binding)
    for _ in range(20):
        try:
            with socketserver.TCPServer(('', PORT + 1), None) as test:
                pass  # next port available, current port is fine
            break
        except OSError:
            time.sleep(0.05)

    # Open in Firefox - use snap path directly for Wayland compatibility
    for candidate in ['/snap/bin/firefox.firefox', '/usr/bin/firefox']:
        try:
            subprocess.Popen([candidate, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Launched with: {candidate}")
            break
        except FileNotFoundError:
            continue
    else:
        # Fallback: try xdg-open
        subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Wait for the HTTP request from Firefox before shutting down.
    # Use a flag set by the handler so we shut down right after the page loads.
    got_request = threading.Event()

    original_log_message = Handler.log_message
    def log_once(self, format, *args):
        if 'GET' in str(format % args) and fname in str(format % args):
            got_request.set()
        return original_log_message(self, format, *args)
    Handler.log_message = log_once

    # Poll for up to 5s until Firefox requests the page
    for _ in range(100):
        if got_request.is_set():
            break
        time.sleep(0.05)

    server.shutdown()
    print("Done.")

if __name__ == "__main__": main()
