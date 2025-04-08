I am doing some parts of my main project (LaeArve) as add-on little projects under the same licence.

I think it's good to have separate little projects, which can be used separately, and then connect them to form one bigger project.

# Markdown-processing Code Server

Using __Pygments__ library:

This allows to navigate code files, where:
- Markdown, in full-line comments, is parsed into Markdown.
- Code is parsed into code blocks.
- The rest is handled intelligently

Using __Mistune__ library:

Additional step:
- Read Markdown and Code files
- Inside code files, add syntax highlighting for Markdown inside inline comments, which were not rendered into Markdown.

Using __Flask__ server library:

Additional step:
- Allow to navigate file tree with this.
- Consider, how could it be added to GitHub markdown viewer?
