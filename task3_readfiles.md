# Task

(the file is __highlighter.py__)

Create, with these classes, one class for task 3:
- Read either Markdown file or output of the Markdown generator
- In code files, once again identify comment positions; add Markdown syntax highlighting inside comments in code blocks, but do not break the rendering of comment syntax itself, such as "TODO:", unless user deliberately does so (by having __TODO__:).

## Update

No, do not change "__" to "**", I have nothing against this comment - do not change any code or comments, only syntax highlight

## Addup

do not process the "__". Instead: can the Pygments comment highlighting of _the same_ language _follow_: this means, if inside the comment there is some important thing for the language itself, it will be highlighted by it's own highlighter - so that this would rather be pre-processor than final word in highlighting. Is this possible?