if re.match(r"^\s*script:\s*$", line):
    indent = len(line) - len(line.lstrip())
    indent_spaces = " " * indent

    # Insert multiline block with correct indentation
    for block_line in NEW_SCRIPT_BLOCK.split("\n"):
        if block_line.strip() == "":
            continue
        updated_lines.append(indent_spaces + block_line)

    i += 1

    # Skip old script block
    while i < len(lines):
        next_line = lines[i]
        next_indent = len(next_line) - len(next_line.lstrip())

        if next_indent <= indent:
            break

        i += 1

    continue