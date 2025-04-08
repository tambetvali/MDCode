# Fourth task

To package it or something.

Okay can you now create app.py for Flask:
- It uses these classes, especially the last one.
- One can browser folders:
  - If it's Markdown file, it's parsed as HTML
  - If it's code file from Pygments-supported list, it will be preprocessed into Markdown, which is parsed as HTML.
  - Users can add hooks to work with block data before they are parsed.

## Follow-up

But I don't see any of the functionality:
- It should use functionality of previous tasks to turn any code file into markdown (with markdown and code blocks); it should on it's own show Markdown files and parse to HTML with Mistune; and it should load Markdown and Code files: and use the other implementation to also syntax-highlight the comments.

## Addition

Notice the order:
- If it's code file, it's converted to Markdown using code from task 2; if it's Markdown, it's used directly
- In each case, code block syntax highlighting uses example 3: also for code blocks normally in Markdown files
