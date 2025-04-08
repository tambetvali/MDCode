# AI Task 1

Parse Python (and other) code into Markdown so that comment positions are identified by line and character, from inside the block and outside the block.

TODO: later one can identify the exact beginnings of lines, I just assume that it's 0 or 1 characters from their first possible beginning, of comment line or of comment.

## Task as given

Parse code files with Pygments so that comment positions are identified by line and character, from inside the block and outside the block.

For example:
- Line comments
  - Inside the block: from beginning of string after comment start char.
  - Outide the block: from the character, which starts the comment identifier.

Block comments:
  - Inside the block: from beginning of string to end of it, inside the comment identifier strings.
  - Outside the block: from beginning of comment to end, from start character of first to end of last comment identifier.

Result:
- All other blocks from start to end are given in string position and line position, where string position is utf-8 or byte character position, and line position is line and char number in utf-8 or byte. Rather, depending on whether str[a] is index based on characters or utf-8 characters in Python, choose the same type for both: utf-8 or byte.
- All the comment blocks
- Everything in one list, where if all those in-betweens are summed, identical copy of initial file would be the result.
- Additionally identify, whether it's full-line comment where comment mark is first position of the line, or whether it's several lines, and beginning is the first position of it's starting line, where end is the last position of it's ending line: mark these as "blc.isBlockComment = True".

API:
- Input: code, codetype (one of Pygments supported types).
- Output: list of comments and strings in between (from last to next comment), with first and last position of each in string position of intput, along with line-character position.
- Could it inherit from Pygments class to load code to be syntax-highlighted, and add "commentblocks" iterator to it, which iterates of tuples of comments with first position before and last after each string, such as: (startPos, commentStr, endPos) using yield: for example, iterComments() would use the loaded pygments class child with input, to return the iterator of comments (yield each) without requiring input itself.

When it's run directly, the following would be produced:
- Test python block with some comments starting from beginning of the line

Notes:
- We need empty lines and empty comments as well, because we use it to parse it into Markdown, where those are paragraph separators.

## ChatGPT overview

I gave my code for it to overview to try to generate proper version of second task with chatgpt, also for it to know it's code:

"""Second block has positions 1:32, like one char after end of first line, but it actually starts from start of the second line"""

### ChatGPT first fix

I added "!!!!!!" where the line number is wrong.

tvali@PC366:~/Laegna/MDCode$ /bin/python3 /home/tvali/Laegna/MDCode/readblocks.py
{'type': 'comment', 'content': '# This is a single-line comment', 'positions': {'string': (0, 31), 'line-char': ((1, 1), (1, 32))}}
{'type': 'code', 'content': '\ndef example_function():\n    """This is a block comment."""\n    print("Hello, world!") ', 'positions': {'string': (31, 118), 'line-char': ((1!!!!!!, 32), (4, 28))}}
{'type': 'comment', 'content': '# Inline comment', 'positions': {'string': (118, 134), 'line-char': ((4, 28), (4, 44))}}
{'type': 'code', 'content': '\n', 'positions': {'string': (134, 135), 'line-char': ((4, 44), (5, 1))}}
{'type': 'comment', 'content': '# Another comment here', 'positions': {'string': (135, 157), 'line-char': ((5, 1), (5, 23))}}
{'type': 'code', 'content': '\n', 'positions': {'string': (157, 158), 'line-char': ((5, 23), (6, 1))}}
tvali@PC366:~/Laegna/MDCode$ 

### ChatGPT final feedback

Well now it start from line 0 and works well (before it started from 1). I will now give you another task.

## Back to copilot with it's original file

### After running the task 2

Verify this code: does it put line feed into end of line, properly, or into beginning of next line, improperly:

...


### Explaining more

I think your logic is wrong.

The next line is "def", which has "\n" at the beginning - it's the line feed of last line. Moreover, it wrongly has the last character of prev line, the line feed, in this second line as a first character. The line feed should be included in the first line, whereas the second line starts from (2, 1) and not with "\n", whereas the first should end with "\n".

### AI Output

What You’re Observing

Your output shows that the second token (of type "code") has content starting with a newline:
```python
'\ndef example_function():\n    """This is a block comment."""\n    print("Hello, world!") '
```

This indicates that the lexer (Pygments) produced that token with a leading newline. In other words, the newline is actually inside the token’s content—not added by your code later. It is not “attached” to the beginning of the new token by your counter logic; it was generated that way.

Your expectation, however, is that the newline should be part of the previous token’s contents (the token that ends that line), such that the next token’s content starts with the first visible character (for example, “def”) and its starting position is (2, 1).

### My task

How we use the code: we keep the blocks together.

If this is the good code from pygments documentation, let's add one more string to the paragraphs: one which is empty for last one or for smaller parts, but contains newline character otherwise.

Otherwise the second class fails or has to parse them too much on their own, duplicating the logic.

### Clarification

Very good, but the newline needs to be separate string, not part of this string - because in some languages, comments end with "*}" for example, and then the line feed must be either inside the comment, or in separate string: we need to express this later for markdown, with {**} not included, and for python separately, so without this fix we lose information.

### Again

You still have errors.

Before I also asked to have three iterators:
- One which clearly separates each full-lines comment, block made of whitespace or block made of code.
- Second, which separates them to code and markdown, where code also takes the markdown blocks connected to it without any whitespace blocks in between: first, mark them markdown, then run additional check which would travel up and down from each code block, and mark them into code block until the first whitespace block not made of comment block.
- Third, iterate over the result and start and end code blocks.
