# Markdown Reader

A lightweight desktop app for reading `.md` files in Firefox with clean, styled rendering. Built as a simple Ubuntu desktop integration — just double-click any markdown file and it opens beautifully rendered.

## Features

- **Zero dependencies** — pure Python3, no pip installs needed
- **Desktop integration** — right-click → "Open With Markdown Reader" on any `.md` file
- **File picker** — runs `zenity` dialog when launched without arguments
- **Snap/Wayland compatible** — works on modern Ubuntu with Firefox snap + Wayland
- **Auto-cleanup** — server shuts down after page loads, no background processes
- **Fresh renders** — re-renders on every open so you always see the latest content

## Installation

```bash
# Make scripts executable
chmod +x mdreader.py mdreader-launcher.sh

# Register as default markdown handler
mkdir -p ~/.local/share/applications
cp mdreader.desktop ~/.local/share/applications/
xdg-mime default mdreader.desktop text/markdown
xdg-mime default mdreader.desktop text/x-markdown

# Optional: set as default for .md files specifically
echo 'text/markdown=mdreader.desktop' >> ~/.config/mimeapps.list
```

## Usage

- **Double-click** any `.md` file in your file manager
- **Run from terminal:** `python3 mdreader.py myfile.md`
- **File picker:** `bash mdreader-launcher.sh` (prompts you to pick a markdown file)

## How It Works

1. Renders markdown to styled HTML (headings, lists, tables, code blocks, blockquotes, links, etc.)
2. Spins up a tiny HTTP server for one request
3. Opens the page in Firefox
4. Server shuts down automatically after the page loads — zero resource drain

## Built With

A pure Python3 markdown-to-HTML converter with no external dependencies. CSS styling is embedded directly in the HTML output.

## Credits

Built running on an RTX 3090 with a local LLM.
