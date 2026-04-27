"""Simple markdown-to-HTML compiler.

This module implements a very small subset of Markdown:

* Heading levels 1-6 using leading ``#`` characters.
* Paragraphs for plain lines.
* Bold text using ``**bold**`` → ``<strong>``.
* Italic text using ``*italic*`` → ``<em>``.
* Links in the form ``[text](url)`` → ``<a href=\"url\">text</a>``.

The implementation is deliberately straightforward and uses regular
expressions; it is **not** a full Markdown spec implementation.

The function ``markdown_to_html`` is fully doctested; run ``python -m doctest -v markdown_compiler/compiler.py``
to verify that all tests pass.
"""

import re
from typing import List

_heading_re = re.compile(r"^(?P<level>#{1,6})\s+(?P<text>.*)$")
_bold_re = re.compile(r"\*\*(?P<text>.+?)\*\*")
_italic_re = re.compile(r"\*(?P<text>.+?)\*")
_link_re = re.compile(r"\[(?P<text>.+?)\]\((?P<url>.+?)\)")


def _replace_inline(md: str) -> str:
    """Replace inline markdown syntax with HTML.

    The order of replacements matters: links first, then bold, then italic.
    """
    # Links
    md = _link_re.sub(r'<a href="\g<url>">\g<text></a>', md)
    # Bold
    md = _bold_re.sub(r'<strong>\g<text></strong>', md)
    # Italic (avoid converting already‑converted bold markers)
    md = _italic_re.sub(r'<em>\g<text></em>', md)
    return md


def markdown_to_html(md: str) -> str:
    """Convert a markdown string to HTML.

    Parameters
    ----------
    md: str
        The markdown source. Lines are separated by ``\n``.

    Returns
    -------
    str
        The resulting HTML. Each block (heading or paragraph) is on its own line.

    Examples
    --------
    >>> markdown_to_html('# Title')
    '<h1>Title</h1>'
    >>> markdown_to_html('Hello **world**')
    '<p>Hello <strong>world</strong></p>'
    >>> markdown_to_html('A *simple* line')
    '<p>A <em>simple</em> line</p>'
    >>> markdown_to_html('[OpenAI](https://openai.com)')
    '<p><a href="https://openai.com">OpenAI</a></p>'
    >>> markdown_to_html('## Section\\nParagraph with **bold** and *italic*')
    '<h2>Section</h2>\\n<p>Paragraph with <strong>bold</strong> and <em>italic</em></p>'
    """
    if not md:
        return ""
    lines: List[str] = []
    for raw_line in md.split('\n'):
        line = raw_line.rstrip('\r')
        if not line.strip():
            # Skip empty lines – they do not produce output in this simple compiler.
            continue
        heading_match = _heading_re.match(line)
        if heading_match:
            level = len(heading_match.group('level'))
            text = _replace_inline(heading_match.group('text').strip())
            lines.append(f"<h{level}>{text}</h{level}>")
        else:
            # Treat everything else as a paragraph.
            text = _replace_inline(line.strip())
            lines.append(f"<p>{text}</p>")
    return "\n".join(lines)

__all__ = ["markdown_to_html"]
