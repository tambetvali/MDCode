# Task 2

Let's get from code file to Markdown file to further process.

File: code2md.py.

TODO: I have to check myself at home and fix the errors. I generate some more code or templates and try to fix the errors later at home.

## Task itself

Now second class:
- It uses the first class to parse code
- It generates Markdown
- It checks, whether the block is spanning only whole lines: no partial lines.
  - If so, it would produce Markdown: if first letter is space, it's omitted, otherwise spacing is included in Markdown output, the exact structure of whitespace in comments.
  - If it's other content between two such, then if it's only whitespace, it does not form code blocks, but is contained in Markdown: it splits the paragraphs of comments.
  - If there are no empty lines or whitespace-only lines between the last comment after such paragraph break and the following code, it's considered part of the code block; also if it's right after the code, with no whitespace between those comment lines and the code, until first whitespace. So the comments need at least one whitespace block between before and after, and the first code block in that direction.
- The rest, which is not _full-line comments_, would be in code block: it has "```<language>" start and "```" ending, where the language must be proper markdown language for any pygments language: preferrably, automatic download (keep or replace) or library would give this conversion list.

Languages: have a list of basic examples, and if it's not in the list, language from Pygments language list is used, queried automatically (to get code block name from pygments name: I noticed from first try that they seemed to be identic in every example, and if it's wrong it's not a Markdown error, but a helpful identifier to fix, a name of less known language for example, or such as Go, which could be also GoLang).

Notes:
- Whitespace-only blocks, which are connected to Markdown, are not put into code blocks.
- From Markdown output, the inner string is used and the comment marks are removed, also the first space if exists. This means: if the comment if "#  Test", the output would be " Test", leaving the other spaces.

### Clarification

You have empty code blocks in between, which is not allowed:

```python

```

### Other one

But the full-line comment before is not connected to code, because it has empty line in between.

### Third one

Output:
"""```python
This is a full-line comment


def example_function():
    """Block comment."""
    print("Hello, world!")
Inline comment
```



Another full-line comment (separated by an empty line)

"""

- In original code, there are no three empty lines, but one, after the code block. This needs to be equal.
- "This is a full-line comment" must be outside of code block and separated by one blank line. If there would not be this empty line, the comments right before code block are connected __into__ the code block. Each comment inside code block still has original comment marks.
- Inline comment should not be on new line, but left untouched.
- We create Markdown only from comments spanning only whole lines, and whitespace lines in between. Any line, which is not whole-line comment, is considered code and put into code block.

### Another clarification

Look, you need this logic:
- Use the iterator to build deeper iterator inside the class:
  - Iterate over block comments (start, comment, end) are like this: for "# Comment", ("comment", "# ", "Comment", ""), which can be decided as o="Markdown"/"Code"; the lines in between: empty lines, or lines with only whitespace, are all connected and marked "whitespace" with their content included, and all the other lines connected and marked "code", with their content included.
  - Several block comments, which have no blocks in between, are united to one in subsequent iterator, and: if whitespace blocks are in between whole-line comments and not connected to blocks, they are marked "markdownwhitespace", but if they are in between of code blocks, they are marked as "codewhitespace". If any of the comment blocks has, before or after, no whitespace blocks, but a code block as next or last block, it's marked as "codecomment".

Other step:
- iterate over this new iterator, and when it outputs comment or markdownwitespace, mark it outside code block, otherwise inside. Finally, start code blocks before each code block, and end after last subsequent code block.

### One more, repeating already :P

Almost fine, but:
- You do not add empty lines with whitespace, but only the ones which exist either inside empty comments, empty lines in comments or code.
- I said do not put inline comments to new line, without comment mark, but include their original form, which in python starts with "#".

### Clarification 4

Here you add empty lines:

"""This is a full-line comment

```python

def example_function():
    """Block comment."""
    print("Hello, world!") 
# Inline comment
```



Another full-line comment (separated by an empty line)
"""

Correct one is this, without random line feeds, because I said parse and not generate: """```python
This is a full-line comment
def example_function():
    """Block comment."""
    print("Hello, world!") 
# Inline comment
```

Another full-line comment (separated by an empty line)
"""

If you parse and do not generate, you notice - the first full-line comment does not have empty lines between it and a code block, so it needs to be inside code block. The last comment has one empty line, and this is converted to one empty line: to not generate any additional content, even whitespace, and keep all the content.
r'''# This is a full-line comment
def example_function():
    """Block comment."""
    print("Hello, world!") # Inline comment

# Another full-line comment (separated by an empty line)'''

## I switched to ChatGPT

I told:

CoPilot failed with this task, not being able to fix its errors; so write the second file of python code:

%% paste of whole this file before this section %%

### Debug request

Create a test file "readblocks.py", which goes through the track of generating those two blocks, and shows the content at each step: where they blank line is added? Is it in the first block, for example, which was parsed?

Output this along with proper output.

### Debug result

From the result you can see:
- Empty blocks come from a block missing \n, whereas the next block is made only of this letter. In the earlier or current file, where the blocks are generated, a mistake needs to be fixed.

== RAW TOKENS ==
[(Token.Comment.Single, '# This is a full-line comment'),
 (Token.Text.Whitespace, '\n'),
 (Token.Keyword, 'def'),
 (Token.Text, ' '),
 (Token.Name.Function, 'example_function'),
 (Token.Punctuation, '('),
 (Token.Punctuation, ')'),
 (Token.Punctuation, ':'),
 (Token.Text.Whitespace, '\n'),
 (Token.Text.Whitespace, '    '),
 (Token.Literal.String.Doc, '"""Block comment."""'),
 (Token.Text.Whitespace, '\n'),
 (Token.Text, '    '),
 (Token.Name.Builtin, 'print'),
 (Token.Punctuation, '('),
 (Token.Literal.String.Double, '"'),
 (Token.Literal.String.Double, 'Hello, world!'),
 (Token.Literal.String.Double, '"'),
 (Token.Punctuation, ')'),
 (Token.Text, '  '),
 (Token.Comment.Single, '# Inline comment'),
 (Token.Text.Whitespace, '\n'),
 (Token.Text.Whitespace, '\n'),
 (Token.Comment.Single,
  '# Another full-line comment (separated by an empty line)'),
 (Token.Text.Whitespace, '\n')]

== CLASSIFIED LINES ==
full_comment  : '# This is a full-line comment\n'
code          : 'def example_function():\n'
code          : '    """Block comment."""\n'
code          : '    print("Hello, world!")  # Inline comment\n'
whitespace    : '\n'
full_comment  : '# Another full-line comment (separated by an empty line)'

== TRANSITIONS ==
Traceback (most recent call last):
  File "/home/tvali/Laegna/MDCode/readblocks_debug.py", line 51, in <module>
    print(f"Prev: {prev:12} -> Curr: {curr:12} | Line: {repr(line)}")
TypeError: unsupported format string passed to NoneType.__format__

### 

### Clarifications to ChatGPT after some work

Rather:
- Do not add empty lines
- If there is no empty line between comment and code, it needs to be inside code block with comment marks
- If there is empty line between comment and code, the comment marks are removed, and first space of the line if exists, and Markdown is generated.
- No empty lines are added or removed, but empty lines between markdown comment blocks are part of them, and empty lines inside a code block is part of them: so, to separate two markdown paragraphs, one could add empty line or empty comment, and no code blocks would appear.

### More :)

This is backwards:
- The first full line comment needs to be inside code block, and then have a "#", because there is no empty line between it and the code.
- The second one needs to be outside, with black line in between, and without "# ", as there is blank block in between.

== SIMULATED MARKDOWN OUTPUT ==
This is a full-line comment
```python
    def example_function():

    # Another full-line comment (separated by an empty line)
```

## CoPilot

Now back to CoPilot ..ChatGPT ran into the same problems: so it's a deeper bug.

### My feedback

inline comment, as I told you repeatedly, is *not parsed to separate line or given any other form than in original code*

