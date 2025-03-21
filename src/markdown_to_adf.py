import re

def markdown_to_adf(markdown):
    lines = markdown.split('\n')
    adf_content = []

    bullet_list = []

    def flush_bullets():
        nonlocal bullet_list
        if bullet_list:
            adf_content.append({
                "type": "bulletList",
                "content": bullet_list
            })
            bullet_list = []

    def parse_text(text):
        nodes = []
        while text:
            bold_match = re.search(r"\*\*(.*?)\*\*", text)
            if bold_match:
                pre = text[:bold_match.start()]
                if pre:
                    nodes.append({ "type": "text", "text": pre })

                nodes.append({
                    "type": "text",
                    "text": bold_match.group(1),
                    "marks": [{ "type": "strong" }]
                })
                text = text[bold_match.end():]
            else:
                nodes.append({ "type": "text", "text": text })
                break
        return nodes

    for line in lines:
        line = line.rstrip()

        if line.startswith('### '):
            flush_bullets()
            adf_content.append({
                "type": "heading",
                "attrs": { "level": 3 },
                "content": [{ "type": "text", "text": line[4:] }]
            })
        elif line.startswith('## '):
            flush_bullets()
            adf_content.append({
                "type": "heading",
                "attrs": { "level": 2 },
                "content": [{ "type": "text", "text": line[3:] }]
            })
        elif line.startswith('- '):
            bullet_list.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": parse_text(line[2:])
                }]
            })
        elif line.strip() == '':
            flush_bullets()
        else:
            flush_bullets()
            adf_content.append({
                "type": "paragraph",
                "content": parse_text(line)
            })

    flush_bullets()

    return {
        "type": "doc",
        "version": 1,
        "content": adf_content
    }
