import json
import re

from docling.document_converter import DocumentConverter

DOCX_PATH = "sample.docx"
OUTPUT_PATH = "result.json"


EXERCISE_PATTERNS = [
    r"^exercise[s]?$",
    r"^answer the following",
    r"^choose the right answer",
    r"^distinguish between",
    r"^project\s*/?\s*activity$",
    r"^project\s+activity$",
]


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def is_exercise_start(text):
    text = text.lower().strip()
    return any(re.match(pattern, text) for pattern in EXERCISE_PATTERNS)


def is_figure_heading(text):
    return bool(
        re.match(
            r"^(fig\.?|figure|map|table|plate|box)\s*[\d\-.:]?",
            text,
            re.IGNORECASE,
        )
    )


def is_heading(text, label):
    label = label.lower()
    words = text.split()

    if label in {
        "title",
        "document_title",
        "section_header",
        "section-header",
        "heading",
    }:
        return True

    if re.match(r"^(unit|chapter)[-\s]?\w+", text, re.IGNORECASE):
        return True

    if re.match(r"^(i|ii|iii|iv|v|vi|vii|viii|ix|x)[.)]\s+", text, re.IGNORECASE):
        return True

    if text.isupper() and 2 <= len(words) <= 15:
        return True

    return False


def get_heading_level(text, label):
    if re.match(r"^unit[-\s]?\w+", text, re.IGNORECASE):
        return 1

    if re.match(r"^chapter[-\s]?\w+", text, re.IGNORECASE):
        return 2

    if re.match(
        r"^(i|ii|iii|iv|v|vi|vii|viii|ix|x)[.)]\s+",
        text,
        re.IGNORECASE,
    ):
        return 4

    if label.lower() in {"title", "document_title"}:
        return 1

    return 3


def create_node(node_type, title):
    return {
        "type": node_type,
        "title": title,
        "content": [],
        "children": [],
    }


def main():
    print("Passing DOCX to Docling...")

    converter = DocumentConverter()
    result = converter.convert(DOCX_PATH)
    document = result.document

    root = {
        "type": "document",
        "title": "Fundamentals of Human Geography",
        "children": [],
    }

    stack = [(0, root)]
    inside_exercises = False
    chapter_has_title = False

    for item, _ in document.iterate_items():
        label = str(getattr(item, "label", "")).lower()
        text = getattr(item, "text", None)

        if not text:
            continue

        text = clean_text(text)

        if not text:
            continue

        if label in {"picture", "figure", "caption", "image", "formula"}:
            continue

        if re.fullmatch(r"\d+", text):
            continue

        if text.lower() == "fundamentals of human geography":
            continue

        if is_figure_heading(text):
            continue

        if is_exercise_start(text):
            inside_exercises = True
            continue

        if inside_exercises:
            if is_heading(text, label):
                inside_exercises = False
            else:
                continue

        if is_heading(text, label):
            level = get_heading_level(text, label)

            if level == 2:
                chapter_has_title = False

            if level == 3 and not chapter_has_title:
                for current_level, current_node in reversed(stack):
                    if current_node["type"] == "chapter":
                        current_node["title"] = text
                        chapter_has_title = True
                        break
                else:
                    node = create_node("section", text)
                    root["children"].append(node)
                    stack = [(0, root), (3, node)]
                continue

            if level == 1:
                node_type = "unit"
            elif level == 2:
                node_type = "chapter"
            elif level == 3:
                node_type = "section"
            else:
                node_type = "subsection"

            node = create_node(node_type, text)

            while stack and stack[-1][0] >= level:
                stack.pop()

            parent = stack[-1][1]
            parent["children"].append(node)

            stack.append((level, node))
            continue

        current_node = stack[-1][1]

        if current_node["type"] == "document":
            root.setdefault("content", []).append(text)
        else:
            current_node["content"].append(text)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(root, file, ensure_ascii=False, indent=2)

    print(f"Done: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
