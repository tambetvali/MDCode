from pygments.lexers import get_lexer_by_name
from pygments.token import Token
from pygments import lex
import pprint

# Sample input source code
test_code = '''# This is a full-line comment
def example_function():
    """Block comment."""
    print("Hello, world!")  # Inline comment

# Another full-line comment (separated by an empty line)'''

# Tokenize the input
lexer = get_lexer_by_name("python")
tokens = list(lex(test_code, lexer))

# Step 1: Classify Each Block (Code or Markdown)
def classify_blocks(code):
    lines = code.splitlines(keepends=True)
    result = []
    
    # Classify blocks as code, markdown, or whitespace
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append(("whitespace", line))
        elif stripped.startswith("#"):
            result.append(("full_comment", line))
        else:
            result.append(("code", line))
    return result

line_blocks = classify_blocks(test_code)

print("\n== CLASSIFIED BLOCKS ==")
for kind, line in line_blocks:
    print(f"{kind:14}: {repr(line)}")

# Step 2: Assign Attributes ("code" and "markdown")
def assign_code_markdown(line_blocks):
    result = []
    inside_code = False
    last_was_comment = False

    for i, (kind, line) in enumerate(line_blocks):
        if kind == "code":
            if not inside_code:
                result.append("start_code")  # Start of a code block
                inside_code = True
            result.append(f"code: {line.strip()}")  # Add the actual code line

        elif kind == "full_comment":
            if inside_code:
                result.append(f"code: {line.strip()}")  # Comment inside code block
            else:
                result.append(f"markdown: {line.strip('# ').strip()}")  # Comment outside, as markdown
            last_was_comment = True

        elif kind == "whitespace":
            if last_was_comment:
                result.append("end_code")  # End code block if whitespace follows comment
            result.append("whitespace")  # Keep track of whitespace

    if inside_code:
        result.append("end_code")  # End the last code block

    return result

classified_with_attributes = assign_code_markdown(line_blocks)

print("\n== ASSIGNED ATTRIBUTES ==")
for item in classified_with_attributes:
    print(item)

# Step 3: Process and Format Markdown (Create Final Output)
def process_and_generate_markdown(classified_with_attributes):
    markdown_output = []
    inside_code = False

    for item in classified_with_attributes:
        if item == "start_code":
            markdown_output.append("```python")  # Start of code block
            inside_code = True
        elif item == "end_code":
            markdown_output.append("```")  # End of code block
            inside_code = False
        elif item.startswith("code:"):
            markdown_output.append(item[5:])  # Add code without the prefix
        elif item.startswith("markdown:"):
            markdown_output.append(item[9:])  # Add markdown comment without "#"
        elif item == "whitespace":
            markdown_output.append("")  # Keep empty lines for separation

    return "\n".join(markdown_output)

final_markdown = process_and_generate_markdown(classified_with_attributes)

print("\n== SIMULATED MARKDOWN OUTPUT ==")
print(final_markdown)
