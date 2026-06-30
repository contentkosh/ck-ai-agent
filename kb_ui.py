import gradio as gr

from services.kb_ingestion_service import ingest_documents


# -------------------------
# UI FUNCTION
# -------------------------
def upload_knowledge_base(files, tag):
    """
    Upload PDF documents to the Knowledge Base.
    """

    if not files:
        return "Please upload at least one PDF."

    if not tag or not tag.strip():
        return "Please enter a metadata tag."

    return ingest_documents(files, tag.strip())


# -------------------------
# GRADIO UI
# -------------------------
with gr.Blocks(title="Knowledge Base Management System") as app:

    gr.Markdown("# Knowledge Base Management System")
    gr.Markdown("Upload PDF documents into the Qdrant Vector Database.")

    pdf_upload = gr.File(
        label="Upload PDFs",
        file_types=[".pdf"],
        file_count="multiple"
    )

    tag_input = gr.Textbox(
        label="Metadata Tag",
        placeholder="Example: cyber, healthcare, finance"
    )

    upload_button = gr.Button("Upload to Knowledge Base")

    output_box = gr.Textbox(
        label="Upload Status",
        lines=10
    )

    upload_button.click(
        fn=upload_knowledge_base,
        inputs=[pdf_upload, tag_input],
        outputs=output_box
    )


if __name__ == "__main__":
    app.launch(
        server_name="127.0.0.1",
        server_port=7860
    )