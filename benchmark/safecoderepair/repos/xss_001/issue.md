# Bug: HTML escaping omits double-quote escaping

`escape_html()` escapes `<`, `>`, and `&` but not `"`. When a username like
`alice" onclick="evil()` is placed in a `data-author="..."` attribute by
`render_comment`, the unescaped quote breaks out of the attribute context.

Add `.replace('"', '&quot;')` to the escaping chain in `escape_html`.
