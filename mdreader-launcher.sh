#!/usr/bin/env bash
# Markdown Reader Launcher - opens .md files via mdreader.py as a desktop app
set -e

if [ $# -eq 0 ]; then
    # No file passed: open a file picker dialog to select a markdown file
    selected=$(zenity --file-selection --title="Open Markdown File" --file-filter='*.md *.markdown' 2>/dev/null)
    if [ -z "$selected" ]; then exit 0; fi
    python3 /home/pawan/mdreader.py "$selected" &
else
    # File passed from desktop association
    for f in "$@"; do
        case "$f" in
            *.md|*.markdown) python3 /home/pawan/mdreader.py "$f" & ;;
            *)
                # Directory passed: open a file picker inside that directory
                if [ -d "$f" ]; then
                    selected=$(zenity --file-selection --title="Open Markdown File" --filename="$f" --file-filter='*.md *.markdown' 2>/dev/null)
                    if [ -z "$selected" ]; then continue; fi
                    python3 /home/pawan/mdreader.py "$selected" &
                else
                    echo "Not a markdown file: $f (double-click only works with .md files)"
                fi
                ;;
        esac
    done
fi

# Keep script alive so Firefox stays open (backgrounded mdreader.py runs its own loop)
wait 2>/dev/null || true
