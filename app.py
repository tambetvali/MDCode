#!/usr/bin/env python3
"""
app.py – A Flask application to browse folders and process files.

Processing order:
  • If the file is a code file (e.g., ".py"), it is converted to Markdown using the MarkdownGenerator
    (Task 2). The language used is determined via the Shtype class (which queries Pygments).
  • If the file is a Markdown file (".md" or ".markdown"), its raw content is used directly.
  • In both cases, the resulting Markdown is then processed by the Task3Highlighter (Task 3) to re‑highlight
    code blocks (which injects HTML markup for syntax highlighting, including for comments).
  • Finally, the combined Markdown (now containing embedded HTML for code blocks) is converted to HTML via Mistune.
  
Additionally, the folder view displays the language name next to code files, again using Shtype.

Required packages:
    pip install flask mistune pygments

Custom modules:
    code2md.py, task3.py, shtype.py must be in the same directory.
"""

import os
import logging
from flask import Flask, request, redirect, url_for
import mistune

# Set up basic logging.
logging.basicConfig(level=logging.DEBUG)

# Base directory for file browsing; adjust as needed.
BASE_DIR = os.getcwd()

# File extension sets.
MD_EXTENSIONS   = {".md", ".markdown"}
CODE_EXTENSIONS = {".py", ".js", ".java", ".c", ".cpp", ".go", ".html", ".css"}

# Import custom classes.
try:
    from code2md import MarkdownGenerator
except ImportError:
    MarkdownGenerator = None
    logging.error("Could not import MarkdownGenerator from code2md.py")
try:
    from task3 import Task3Highlighter
except ImportError:
    Task3Highlighter = None
    logging.error("Could not import Task3Highlighter from task3.py")
try:
    from shtype import Shtype
except ImportError:
    Shtype = None
    logging.error("Could not import Shtype from shtype.py")

# Instantiate Shtype to map file extensions to language names.
if Shtype is not None:
    shtype_checker = Shtype()
else:
    shtype_checker = None

# Global hooks list (each hook is a callable: blocks -> blocks)
pre_parse_hooks = []

def run_pre_parse_hooks(blocks):
    for hook in pre_parse_hooks:
        blocks = hook(blocks)
    return blocks

app = Flask(__name__)

# ---------------------------------------------------------------------
# Folder browsing routes.
# ---------------------------------------------------------------------
@app.route('/', defaults={'subpath': ''})
@app.route('/browse/', defaults={'subpath': ''})
@app.route('/browse/<path:subpath>')
def browse(subpath):
    abs_path = os.path.join(BASE_DIR, subpath)
    if not os.path.exists(abs_path):
        return f"Path {abs_path} not found", 404
    if os.path.isfile(abs_path):
        return redirect(url_for('view_file', subpath=subpath))
    items = sorted(os.listdir(abs_path), key=lambda s: s.lower())
    html_items = []
    parent = os.path.dirname(subpath)
    if subpath:
        html_items.append(f'<li><a href="{url_for("browse", subpath=parent)}">.. (Parent Directory)</a></li>')
    for item in items:
        item_abs = os.path.join(abs_path, item)
        item_rel = os.path.join(subpath, item)
        display_text = item
        if os.path.isfile(item_abs):
            ext = os.path.splitext(item)[1].lower()
            if ext in CODE_EXTENSIONS and shtype_checker is not None:
                langs = shtype_checker.get_languages_by_extension(ext)
                if langs:
                    display_text += f" (lang: {langs[0]})"
        if os.path.isdir(item_abs):
            html_items.append(f'<li>[DIR] <a href="{url_for("browse", subpath=item_rel)}">{display_text}</a></li>')
        else:
            html_items.append(f'<li>[FILE] <a href="{url_for("view_file", subpath=item_rel)}">{display_text}</a></li>')
    html = f"<h1>Index of /{subpath}</h1><ul>" + "\n".join(html_items) + "</ul>"
    return html

# ---------------------------------------------------------------------
# File viewing route.
# ---------------------------------------------------------------------
@app.route('/view/<path:subpath>')
def view_file(subpath):
    abs_path = os.path.join(BASE_DIR, subpath)
    if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
        return f"File {abs_path} not found", 404

    ext = os.path.splitext(abs_path)[1].lower()
    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()

    md_content = None

    if ext in MD_EXTENSIONS:
        # For Markdown files: use the file content directly.
        logging.debug("File identified as Markdown.")
        md_content = content
    elif ext in CODE_EXTENSIONS:
        # For code files: use MarkdownGenerator (Task 2) to convert code into Markdown.
        logging.debug("File identified as a code file.")
        language = ext[1:]  # default to extension without dot
        if shtype_checker is not None:
            langs = shtype_checker.get_languages_by_extension(ext)
            if langs:
                language = langs[0]
        logging.debug(f"Determined language for code file: {language}")
        if MarkdownGenerator is None:
            logging.error("MarkdownGenerator class not available. Showing plain content.")
            md_content = "```\n" + content + "\n```"
        else:
            md_gen = MarkdownGenerator(content, language)
            md_content = md_gen.generate_markdown()
            logging.debug("Markdown conversion via MarkdownGenerator complete.")
    else:
        # For unsupported file types, display plain text.
        logging.debug("File type not recognized for Markdown processing; showing plain text.")
        return f"<pre>{content}</pre>"

    # In both cases (Markdown file or generated Markdown) we now process code blocks.
    # Task3Highlighter (Task 3) replaces fenced code blocks with HTML (using Pygments for syntax highlighting).
    if Task3Highlighter is None:
        logging.error("Task3Highlighter class not available; skipping further processing.")
        processed_md = md_content
    else:
        highlighter = Task3Highlighter(md_content)
        processed_md = highlighter.process()
        logging.debug("Processing with Task3Highlighter complete.")

    # Finally, run the result through a Markdown-to-HTML converter (using Mistune).
    # We disable escaping so that embedded HTML (from Task3Highlighter) isn't escaped.
    final_html = mistune.markdown(processed_md, escape=False)
    logging.debug("Conversion to final HTML complete.")

    html_template = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <title>{subpath}</title>
        <style>
          body {{ font-family: sans-serif; margin: 2em; }}
          pre {{ background-color: #f5f5f5; padding: 1em; overflow-x: auto; }}
          code {{ font-family: monospace; }}
        </style>
      </head>
      <body>
        {final_html}
        <hr>
        <p><a href="{url_for('browse', subpath=os.path.dirname(subpath))}">Back to Directory</a></p>
      </body>
    </html>
    """
    return html_template

# ---------------------------------------------------------------------
# Hook management endpoint.
# ---------------------------------------------------------------------
@app.route('/hooks/add', methods=["POST"])
def add_hook():
    hook_name = request.form.get("name", "UnnamedHook")
    def new_hook(blocks):
        app.logger.debug(f"Hook {hook_name} called with {len(blocks)} blocks.")
        # Optionally modify blocks here.
        return blocks
    pre_parse_hooks.append(new_hook)
    return f"Added hook {hook_name}", 200

# ---------------------------------------------------------------------
# Run the application.
# ---------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
