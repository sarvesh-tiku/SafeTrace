def parse_line(line: str) -> list[str]:
    """Parse a CSV line, handling quoted fields."""
    fields: list[str] = []
    current = ""
    in_quotes = False

    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            in_quotes = not in_quotes
            # BUG: does not skip the quote character, includes it in field
            current += ch
        elif ch == "," and not in_quotes:
            fields.append(current)
            current = ""
        else:
            current += ch
        i += 1

    fields.append(current)
    return fields


def parse_csv(text: str) -> list[list[str]]:
    """Parse multi-line CSV text."""
    return [parse_line(line) for line in text.strip().splitlines()]
