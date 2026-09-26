import json
import re
import docx


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def detect_chapter(text):
    match = re.match(r"^Chapter\s*[-:]?\s*(\d+)\b", text, re.IGNORECASE)
    return match.group(1) if match else None


def detect_unit(text):
    return re.match(
        r"^Unit\s*[-:]?\s*(?:[IVXLCDM]+|\d+)\b",
        text,
        re.IGNORECASE,
    )


def chunk_by_chapter(file_path, output_json_path="chapter_chunks.json"):
    """
    Reads a .docx document and groups all text between Chapter-X
    boundaries into chapter-level JSON chunks.
    """
    try:
        doc = docx.Document(file_path)
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    chunks = []
    current_chapter = None
    current_title = None
    current_content = []
    waiting_for_title = False

    for para in doc.paragraphs:
        text = clean_text(para.text)

        if not text:
            continue

        chapter_number = detect_chapter(text)

        # New chapter detected
        if chapter_number:
            if current_chapter is not None:
                chunks.append(
                    {
                        "chapter": current_chapter,
                        "title": current_title or "",
                        "content": " ".join(current_content),
                    }
                )

            current_chapter = f"Chapter-{chapter_number}"
            current_title = None
            current_content = []
            waiting_for_title = True
            continue

        # Ignore everything before the first chapter
        if current_chapter is None:
            continue

        # First meaningful paragraph after Chapter-X = chapter title
        if waiting_for_title:
            current_title = text
            waiting_for_title = False
            continue

        # Everything else belongs to this chapter
        current_content.append(text)

    # Save final chapter
    if current_chapter is not None:
        chunks.append(
            {
                "chapter": current_chapter,
                "title": current_title or "",
                "content": " ".join(current_content),
            }
        )

    structured_data = {
        "document_metadata": {
            "source_file": file_path,
            "total_chapters": len(chunks),
        },
        "chunks": [
            {
                "chunk_id": i + 1,
                "chapter": item["chapter"],
                "title": item["title"],
                "content": item["content"],
            }
            for i, item in enumerate(chunks)
        ],
    }

    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(
            structured_data,
            json_file,
            indent=4,
            ensure_ascii=False,
        )

    print(
        f"Successfully extracted {len(chunks)} chapters " f"into '{output_json_path}'."
    )


if __name__ == "__main__":
    chunk_by_chapter(
        file_path="Geography_compressed.docx",
        output_json_path="chapter_output.json",
    )
