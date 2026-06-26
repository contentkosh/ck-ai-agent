import gradio as gr

from service.kb_ingest import ingest_documents


# -------------------------
# UI FUNCTION
# -------------------------

def upload_knowledge_base(files, tag):

    if not files:
        return "Please upload PDFs"

    if not tag:
        return "Please enter a tag"

    result = ingest_documents(
        files,
        tag
    )

    return result


# -------------------------
# GRADIO UI
# -------------------------

with gr.Blocks() as app:

    gr.Markdown(
        "# Knowledge Base Management System"
    )

    gr.Markdown(
        "Upload PDFs into Qdrant Vector Database"
    )

    pdf_upload = gr.File(
        file_count="multiple",
        file_types=[".pdf"],
        label="Upload PDFs"
    )

    tag_input = gr.Textbox(
        label="Metadata Tag",
        placeholder="Example: cyber, healthcare, finance"
    )

    upload_button = gr.Button(
        "Upload to Knowledge Base"
    )

    output_box = gr.Textbox(
        label="Upload Status",
        lines=10
    )

    upload_button.click(
        fn=upload_knowledge_base,
        inputs=[
            pdf_upload,
            tag_input
        ],
        outputs=output_box
    )

app.launch()