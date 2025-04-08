#!/usr/bin/env python3
"""
task3.py – A pre‑processor that processes Markdown output by re‑processing
fenced code blocks. In each code block, it processes comment lines for deliberate
markers while skipping shebang lines (e.g. "#!/usr/bin/env python3"), which are left unchanged.

Behavior:
  • Reads a Markdown text (from a file or a string).
  • Locates fenced code blocks (delimited by triple backticks).
  • For each code block, processes its content line‑by‑line.
      - If a line, after stripping leading whitespace, starts with "#!" (a shebang),
        that line is passed through unchanged.
      - If a comment line (starting with "#" after stripping whitespace) is found,
        then any deliberate marker matching the regex pattern __WORD__:
        is wrapped in a <span> tag for highlighting.
      - Other lines are left unchanged.
  • Reassembles and outputs the modified Markdown text.
  
No content is otherwise modified.
"""

import re

class Task3Highlighter:
    def __init__(self, markdown_text):
        self.markdown_text = markdown_text

    def process_code_block(self, code_text):
        """
        Process the content of a code block.

        For each line in the code block:
          - If the line, after stripping whitespace, starts with "#!",
            do not process it (leave it unchanged).
          - Otherwise, if the line is a comment line (its first non‑whitespace character is "#"),
            process it by wrapping any deliberate marker of the form __WORD__:
            in a <span class="highlight">...</span>.
          - All other lines are left unchanged.
        Returns the processed code block as a single string.
        """
        # Compile a regex pattern that matches a deliberate marker:
        # Two underscores, one or more word characters, two underscores, immediately followed by a colon.
        marker_pattern = re.compile(r'__(\w+)__(:)')
        processed_lines = []
        for line in code_text.split("\n"):
            stripped = line.lstrip()
            if stripped.startswith("#!"):
                # This is a shebang line; leave it unchanged.
                processed_lines.append(line)
                continue
            if stripped.startswith("#"):
                # Process deliberate markers in full-line comments.
                # (Inline comments are left unchanged unless they begin at column 1.)
                new_line = marker_pattern.sub(r'<span class="highlight">\g<0></span>', line)
                processed_lines.append(new_line)
            else:
                processed_lines.append(line)
        return "\n".join(processed_lines)

    def process(self):
        """
        Process the entire Markdown text.

        Finds all fenced code blocks (using triple backticks) in the Markdown text.
        For each code block, process the code content with process_code_block(), then reassemble
        the fenced block with its original language identifier (if any).
        Returns the modified Markdown text.
        """
        # Regex to match fenced code blocks:
        #   Group 1: optional language identifier.
        #   Group 2: code block content.
        code_fence_regex = re.compile(r"```(\w*)\n(.*?)\n```", re.DOTALL)

        def replace_block(match):
            language = match.group(1)  # may be empty
            code_content = match.group(2)
            processed_code = self.process_code_block(code_content)
            return f"```{language}\n{processed_code}\n```"

        new_markdown = code_fence_regex.sub(replace_block, self.markdown_text)
        return new_markdown

# Example usage:
if __name__ == "__main__":
    # Example markdown input with two fenced code blocks.
    # The first block includes a shebang line and a comment with a deliberate marker.
    example_markdown = r'''```python
#!/usr/bin/env python3
# This is a full-line comment with a __TODO__:
def example_function():
    """Block comment with a __FIXME__: inside."""
    print("Hello, world!") # Inline comment with __NOTE__:
#!/usr/bin/env python3
# Another full-line comment (separated by an empty line) with a __WARNING__:
```'''
    processor = Task3Highlighter(example_markdown)
    processed_markdown = processor.process()
    print("== Processed Markdown Output ==")
    print(processed_markdown)
