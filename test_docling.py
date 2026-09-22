from pathlib import Path
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("Geography_compressed.docx")
markdown = result.document.export_to_markdown(
    image_placeholder=""
)

Path("docling_output.md").write_text(
    markdown,
    encoding="utf-8",
)