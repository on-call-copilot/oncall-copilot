import re

def markdown_to_adf(markdown):
    lines = markdown.split('\n')
    adf_content = []

    bullet_list = []
    inside_code_block = False
    code_block_language = ""
    code_block_lines = []

    def flush_bullets():
        nonlocal bullet_list
        if bullet_list:
            adf_content.append({
                "type": "bulletList",
                "content": bullet_list
            })
            bullet_list = []

    def flush_code_block():
        nonlocal inside_code_block, code_block_lines, code_block_language
        if inside_code_block:
            adf_content.append({
                "type": "codeBlock",
                "attrs": {
                    "language": code_block_language or "plaintext"
                },
                "content": [{
                    "type": "text",
                    "text": "\n".join(code_block_lines)
                }]
            })
            inside_code_block = False
            code_block_language = ""
            code_block_lines = []

    def parse_text(text):
        nodes = []
        while text:
            # Inline code
            code_match = re.search(r"`(.*?)`", text)
            bold_match = re.search(r"\*\*(.*?)\*\*", text)
            italic_match = re.search(r"_(.*?)_", text)

            matches = [m for m in [code_match, bold_match, italic_match] if m]
            if not matches:
                nodes.append({ "type": "text", "text": text })
                break

            # Get the first match
            match = min(matches, key=lambda m: m.start())

            pre = text[:match.start()]
            if pre:
                nodes.append({ "type": "text", "text": pre })

            match_text = match.group(1)
            if match.re.pattern.startswith(r"\*\*"):
                nodes.append({
                    "type": "text",
                    "text": match_text,
                    "marks": [{ "type": "strong" }]
                })
            elif match.re.pattern.startswith(r"_"):
                nodes.append({
                    "type": "text",
                    "text": match_text,
                    "marks": [{ "type": "em" }]
                })
            elif match.re.pattern.startswith(r"`"):
                nodes.append({
                    "type": "text",
                    "text": match_text,
                    "marks": [{ "type": "code" }]
                })

            text = text[match.end():]
        return nodes

    for line in lines:
        stripped = line.rstrip()

        # Start or end of code block
        if stripped.startswith("```"):
            flush_bullets()
            if not inside_code_block:
                inside_code_block = True
                code_block_language = stripped[3:].strip()
                code_block_lines = []
            else:
                flush_code_block()
            continue

        if inside_code_block:
            code_block_lines.append(stripped)
            continue

        # Headings: # to ######
        heading_match = re.match(r"^(#{1,6})\s+(.*)", stripped)
        if heading_match:
            flush_bullets()
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            adf_content.append({
                "type": "heading",
                "attrs": { "level": level },
                "content": [{ "type": "text", "text": text }]
            })
            continue

        # Bullet List
        if stripped.startswith("- "):
            bullet_list.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": parse_text(stripped[2:])
                }]
            })
            continue

        # Empty line
        if stripped.strip() == "":
            flush_bullets()
            continue

        # Paragraph
        flush_bullets()
        adf_content.append({
            "type": "paragraph",
            "content": parse_text(stripped)
        })

    flush_bullets()
    flush_code_block()

    return {
        "type": "doc",
        "version": 1,
        "content": adf_content
    }
