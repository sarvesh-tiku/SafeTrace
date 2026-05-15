# Bug: Script-tag sanitizer is case-sensitive

`sanitize_content` uses a regex without `re.IGNORECASE`, so `<SCRIPT>alert(1)</SCRIPT>`
and other mixed-case variants are not removed and pass through to the browser.

Add `re.IGNORECASE` to the compiled regex flags.
