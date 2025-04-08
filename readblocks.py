from pygments.lexers import get_lexer_by_name
from pygments.token import Token
from pygments import lex

class PygmentsParser:
    def __init__(self, code, codetype):
        self.code = code
        self.lexer = get_lexer_by_name(codetype)

    def iter_comments_and_blocks(self):
        """
        Yields blocks from the parsed code with separate newline information.

        Each yielded block is a dictionary with keys:
          - "type": either "code" or "comment"
          - "content": the block’s text with any trailing newline(s) removed (unless the entire block is exactly "\n")
          - "newline": if this block ended with any newline, then:
                         • if the entire block is exactly "\n", then newline is "", and content remains "\n"
                         • otherwise, newline is set to "\n"
          - "positions": dictionary containing the positions (both string and line-char ranges).

        This separation makes it easier later (for Markdown generation, etc.) to decide how the newline belongs.
        """
        tokens = list(lex(self.code, self.lexer))
        position = 0
        line = 1
        column = 1

        current_block = []
        current_type = None
        start_position = 0
        start_line = 1
        start_col = 1

        for token_type, value in tokens:
            token_lines = value.splitlines(keepends=True)
            token_len = len(value)

            # Save the current line/column BEFORE processing the token.
            token_start_line = line
            token_start_col = column

            new_type = "comment" if token_type in Token.Comment else "code"

            if new_type != current_type and current_block:
                full_text = "".join(current_block)
                # Separate any trailing newline(s) from the content.
                if full_text.endswith("\n"):
                    if full_text == "\n":
                        # The entire block is just the newline; keep it in content.
                        content = full_text
                        newline = ""
                    else:
                        content = full_text.rstrip("\n")
                        newline = "\n"
                else:
                    content = full_text
                    newline = ""
                yield {
                    "type": current_type,
                    "content": content,
                    "newline": newline,
                    "positions": {
                        "string": (start_position, position),
                        "line-char": ((start_line, start_col), (token_start_line, token_start_col))
                    }
                }
                current_block = []
                start_position = position
                start_line = token_start_line
                start_col = token_start_col

            current_type = new_type
            current_block.append(value)
            position += token_len

            # Update line/column counters using the token's parts.
            for part in token_lines:
                if "\n" in part:
                    line += part.count("\n")
                    column = 1
                else:
                    column += len(part)

        if current_block:
            full_text = "".join(current_block)
            if full_text.endswith("\n"):
                if full_text == "\n":
                    content = full_text
                    newline = ""
                else:
                    content = full_text.rstrip("\n")
                    newline = "\n"
            else:
                content = full_text
                newline = ""
            yield {
                "type": current_type,
                "content": content,
                "newline": newline,
                "positions": {
                    "string": (start_position, position),
                    "line-char": ((start_line, start_col), (line, column))
                }
            }

if __name__ == "__main__":
    example_code = """
# This is a single-line comment
def example_function():
    \"\"\"This is a block comment.\"\"\"
    print("Hello, world!") # Inline comment
# Another comment here
"""
    parser = PygmentsParser(example_code, "python")
    for block in parser.iter_comments_and_blocks():
        print(block)
