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

# Step 1: Print raw tokens
print("\n== RAW TOKENS ==")
pprint.pprint(tokens)

# Step 2: Group into lines and categorize
def classify_lines(code):
    lines = code.splitlines(keepends=True)
    result = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            result.append(("whitespace", line))
        elif stripped.startswith("#") and not line.lstrip().startswith("# "):
            # Handles things like #region or #! etc, treat specially if needed
            result.append(("full_comment", line))
        elif line.lstrip().startswith("#"):
            result.append(("full_comment", line))
        else:
            result.append(("code", line))
    return result

line_blocks = classify_lines(test_code)

print("\n== CLASSIFIED LINES ==")
for kind, line in line_blocks:
    print(f"{kind:14}: {repr(line)}")

# Step 3: Show transitions and where blank lines are
print("\n== TRANSITIONS ==")
for i in range(len(line_blocks)):
    prev = line_blocks[i - 1][0] if i > 0 else None
    curr = line_blocks[i][0]
    line = line_blocks[i][1]
    print(f"Prev: {prev:12} -> Curr: {curr:12} | Line: {repr(line)}")

# Step 4: Markdown-style simulation
print("\n== SIMULATED MARKDOWN OUTPUT ==")
inside_code = False
for kind, line in line_blocks:
    if kind in ["code"] and not inside_code:
        print("```python")
        inside_code = True
    if kind in ["full_comment", "whitespace"] and inside_code:
        print("```\n")
        inside_code = False
    if kind == "full_comment" and not inside_code:
        print(line.lstrip("# "), end="")
    elif kind == "whitespace" and not inside_code:
        print()
    else:
        print(line, end="")
if inside_code:
    print("```\n")
