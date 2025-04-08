#!/usr/bin/env python3
"""
code2md.py – Generate Markdown from source code using three iterators.

This solution uses three iterators:

1. iter_tokens():
   • Uses the updated PygmentsParser (from readblocks.py) to get blocks.
   • Splits each block into individual “tokens” (each corresponding to one line).
   • Each token is classified as follows:
       - If the line is blank, token_type = "whitespace".
       - If the block’s type is "comment" and the line (after lstrip) begins with "#", token_type = "comment".
         (This is assumed to be a full‑line comment.)
       - Otherwise, token_type = "code" (this includes inline comment parts that remain embedded within a code line).
   • We record for each token the actual text (“content”), the line number, and its starting column.
   
2. classify_modes(tokens):
   • Initially assigns:
       - Mode "code" to tokens whose token_type is "code".
       - Mode "markdown" to tokens whose token_type is "comment" or "whitespace".
   • Then, for every token marked as "code", it propagates that code‐mode to adjacent tokens if they are comment tokens.
     In practice, if a code token occurs without an intervening whitespace token, then the preceding and following comment tokens receive mode "code".
   
3. group_tokens(tokens):
   • Groups contiguous tokens (from the result of classify_modes) that have the same mode.
   • When outputting a group:
       - If its mode is "code": join the tokens with newlines, and for any token that is of type "comment" and that starts at column 1, strip the leading comment marker (“#” and one following space, if any). Then wrap the group in a fenced code block (using a language identifier determined from the codetype).
       - If its mode is "markdown": simply join the tokens with newlines.
   • Groups are separated by exactly one blank line.
   
Inline comment tokens (i.e. those that come from code lines and do not start at column 1) remain unchanged.
Empty tokens (those that are solely whitespace) are used only to break segments.
"""

from readblocks import PygmentsParser
from pygments.lexers import get_lexer_by_name

class MarkdownGenerator:
    def __init__(self, code, codetype):
        self.code = code
        self.codetype = codetype
        self.parser = PygmentsParser(code, codetype)
    
    # --- Iterator 1: Deep Tokens
    def iter_tokens(self):
        """
        Yields tokens derived from the parsed blocks.
        For each block produced by the parser (which has keys "type", "content", "newline", "positions"),
        split the block by newline characters.
        
        Each token is a dict with:
          - "token_type": "comment", "code", or "whitespace"
          - "content": the text of the line (with no newline)
          - "line": the line number (integer)
          - "col": the starting column (integer, taken from the block for the first line; subsequent lines get col 1)
        """
        tokens = []
        for block in self.parser.iter_comments_and_blocks():
            # block["content"] does not include its trailing newline(s)
            # We split on "\n" (the parser already preserved newlines as separate empty tokens if appropriate)
            lines = block["content"].split("\n")
            # Obtain starting position info from block; assume block["positions"]["line-char"][0] is (line, col)
            start_line, start_col = block["positions"]["line-char"][0]
            current_line = start_line
            for i, line in enumerate(lines):
                if line == "":
                    token_type = "whitespace"
                else:
                    if block["type"] == "comment" and line.lstrip().startswith("#"):
                        token_type = "comment"
                    else:
                        token_type = "code"
                tokens.append({
                    "token_type": token_type,
                    "content": line,
                    "line": current_line,
                    "col": start_col if i == 0 else 1
                })
                current_line += 1
            # Note: We do not separately process block["newline"] here;
            # a trailing newline produces an empty token from the splitting.
        return tokens

    # --- Iterator 2: Classify Modes
    def classify_modes(self, tokens):
        """
        Takes the list of tokens (from iter_tokens) and assigns a "mode" to each token.
        
        Initial assignment:
          - If token_type == "code": mode = "code"
          - Otherwise (comment or whitespace): mode = "markdown"
        
        Then, for every token with mode "code", propagate that mode to adjacent tokens if they are comments.
        Propagation stops if there is a whitespace token.
        """
        # Initial assignment:
        for tok in tokens:
            tok["mode"] = "code" if tok["token_type"] == "code" else "markdown"
        
        n = len(tokens)
        for i, tok in enumerate(tokens):
            if tok["mode"] == "code":
                # Propagate upward.
                j = i - 1
                while j >= 0 and tokens[j]["token_type"] == "comment":
                    tokens[j]["mode"] = "code"
                    j -= 1
                # Propagate downward.
                k = i + 1
                while k < n and tokens[k]["token_type"] == "comment":
                    tokens[k]["mode"] = "code"
                    k += 1
        return tokens

    # --- Iterator 3: Group Tokens and Wrap Code Blocks
    def group_tokens(self, tokens):
        """
        Groups contiguous tokens with the same mode into segments.
        Returns a list of segments, each a dict with:
          - "mode": either "code" or "markdown"
          - "text": the result of joining the token contents with "\n"
          
        When joining tokens:
          • For tokens that are comments and with starting col == 1 (i.e. full-line comments)
            and when the segment mode is "code", remove the leading comment marker.
          • Inline comment tokens (col > 1) are left unchanged.
        """
        if not tokens:
            return []
        segments = []
        current_mode = tokens[0]["mode"]
        current_tokens = [tokens[0]]
        for tok in tokens[1:]:
            if tok["mode"] == current_mode:
                current_tokens.append(tok)
            else:
                segments.append({"mode": current_mode, "tokens": current_tokens})
                current_mode = tok["mode"]
                current_tokens = [tok]
        segments.append({"mode": current_mode, "tokens": current_tokens})
        return segments

    def produce_segments_text(self, segments):
        """
        For each segment (a dict with key "mode" and "tokens"), produce the final text.
        If mode is "code", wrap the joined text in a fenced code block using our language mapping.
        Otherwise, output as plain Markdown.
        Joining is done with exactly "\n" between tokens.
        """
        out_segments = []
        for seg in segments:
            # Process tokens:
            lines = []
            for tok in seg["tokens"]:
                txt = tok["content"]
                if tok["token_type"] == "comment" and tok["col"] == 1 and seg["mode"] == "code":
                    # Full-line comment: remove leading "#" and one extra space if present.
                    if txt.startswith("# "):
                        txt = txt[2:]
                    elif txt.startswith("#"):
                        txt = txt[1:]
                lines.append(txt)
            seg_text = "\n".join(lines).rstrip("\n")
            if seg["mode"] == "code":
                lang = self._get_markdown_language(self.codetype)
                seg_text = f"```{lang}\n{seg_text}\n```"
            out_segments.append(seg_text)
        # Join segments with exactly one blank line
        return "\n\n".join(out_segments)

    def generate_markdown(self):
        # First iterator: get deep tokens.
        tokens = self.iter_tokens()
        # Second iterator: classify tokens into modes.
        tokens = self.classify_modes(tokens)
        # Third: group tokens into segments.
        segments = self.group_tokens(tokens)
        # Then produce final output text.
        return self.produce_segments_text(segments)

    def _get_markdown_language(self, codetype):
        language_map = {
            "python": "python",
            "javascript": "javascript",
            "java": "java",
            "html": "html",
            "css": "css",
            "go": "go",
        }
        if codetype in language_map:
            return language_map[codetype]
        try:
            lexer = get_lexer_by_name(codetype)
            if lexer.aliases:
                return lexer.aliases[0]
        except Exception:
            pass
        return "plaintext"

if __name__ == "__main__":
    example_code = r'''# This is a full-line comment
def example_function():
    """Block comment."""
    print("Hello, world!") # Inline comment

# Another full-line comment (separated by an empty line)'''
    generator = MarkdownGenerator(example_code, "python")
    md_output = generator.generate_markdown()
    print("== FINAL MARKDOWN OUTPUT ==")
    print(md_output)
    with open("output.md", "w") as f:
        f.write(md_output)
