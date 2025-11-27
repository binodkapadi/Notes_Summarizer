import os
import tempfile
from io import BytesIO
from pathlib import Path

import google.generativeai as genai
import streamlit as st
from docx import Document
from dotenv import load_dotenv
from pptx import Presentation

# Load environment variables
load_dotenv()

# Configure Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Mapping between human‑friendly names and Gemini model IDs
MODEL_OPTIONS = {
    "Gemini 2.0 Flash": "gemini-2.0-flash",
    "Gemini 2.0 Flash-Lite": "gemini-2.0-flash-lite",
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Gemini 2.5 Flash-Lite": "gemini-2.5-flash-lite",
}


def summarize_notes(all_text: str, gemini_files, model_name: str, has_pdf: bool) -> str:
    """
    Call Gemini to create thorough, human‑friendly study notes from text + uploaded files.
    """
    if not all_text and not gemini_files:
        raise ValueError("No content provided to summarize.")

    model = genai.GenerativeModel(model_name)

    system_prompt = """
    You are an expert study assistant.
    Analyze the entire content of the uploaded PDF, DOCX, PPT, image, text file, or pasted notes.
    Carefully extract every topic and sub-topic present in the material.

    For the final answer:
    - Organize everything **topic wise** with clear, meaningful headings.
    - For each topic:
        - Write one or more short paragraphs in clear, human-friendly, and easy-to-read language.
        - Use simple wording so even beginners can understand.
        - Add bullet points or sub-headings wherever they make the explanation easier to follow.
    - Maintain proper spacing, alignment, and formatting so the notes look neat and professional.
    - Use clean Markdown formatting in the output (headings, paragraphs, and bullet lists).

    If the document contains comparisons, pros/cons, or differences:
    - Detect them across the whole content.
    - Present the comparison in a structured format similar to the original
      (tables, bullet lists, or grouped sections), but rewritten in simpler,
      more readable language.

    Important rules:
    - Do NOT skip or ignore any topic or sub-topic, even if it looks minor.
    - If the same idea appears many times, merge and summarize it once, clearly.
    - Combine information from all sources provided (PDFs, documents, slides, images,
      text files, and pasted notes) into **one coherent set of notes**.
    - Use ONLY the information given in the notes; do not invent extra facts.
    - Do NOT add extra commentary about being an AI model.
    """

    contents = [system_prompt]

    if all_text.strip():
        contents.append(all_text.strip())

    # Attach uploaded PDF / image files for multimodal summarization
    contents.extend(gemini_files)

    response = model.generate_content(contents)
    return (response.text or "").strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a Word .docx file."""
    doc = Document(BytesIO(file_bytes))
    parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(parts)


def extract_text_from_pptx(file_bytes: bytes) -> str:
    """Extract plain text from a PowerPoint .pptx file."""
    prs = Presentation(BytesIO(file_bytes))
    texts = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                t = shape.text.strip()
                if t:
                    texts.append(t)
    return "\n".join(texts)


def render_footer():
    """Render a footer at the bottom of the page (always visible)."""
    st.markdown(
        """
        <div class="app-footer">
            <p class="footer-text">
                Copyright © by
                <span class="footer-name">Binod Kapadi</span>
            </p>
            <p class="footer-text">All Rights Reserved — 2024</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.title("📝 Notes Summarizer")

    # Optional dark mode CSS
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Check existing uploaded files in session to decide whether to disable text input
    uploaded_files_state = st.session_state.get("file_uploader")

    # Text input (shown first; disabled when any files are already uploaded)
    text_content = st.text_area(
        "📘 Paste your notes here :",
        height=200,
        placeholder="Paste long notes, lecture text, or copied content here...",
        key="notes_text",
        disabled=bool(uploaded_files_state),
    )

    # After reading text, decide whether to disable file uploader
    text_has_content = bool(text_content.strip())

    # File upload: PDFs, Word docs, PowerPoints, text files, and images
    uploaded_files = st.file_uploader(
        "📂 Or upload notes as PDF, Word, PPT, text, or images (limit 10MB per file):",
        type=["pdf", "doc", "docx", "ppt", "pptx", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Limit 10MB per file • Supports PDF, DOC/DOCX, PPT/PPTX, TXT, PNG, JPG.",
        key="file_uploader",
        disabled=text_has_content,
    )

    # Initialize session state for summary
    if "summary" not in st.session_state:
        st.session_state.summary = ""

    # Placeholder for full-page loading overlay
    loader_placeholder = st.empty()

    # Model selection moved just above the Summarize button (no settings icon)
    model_label = st.selectbox("🤖 Select Gemini model:", list(MODEL_OPTIONS.keys()))
    selected_model = MODEL_OPTIONS[model_label]

    if st.button("✨ Summarize"):
        if not text_content.strip() and not uploaded_files:
            st.warning("⚠️ Please provide some notes or upload at least one file.")
        else:
            # Clear previous summary so old notes disappear while new summary is being generated
            st.session_state.summary = ""
            # Show custom blurred overlay loader
            loader_html = """
            <div class="overlay-loader">
                <div class="overlay-loader-circle"></div>
                <p class="overlay-loader-text">Summarizing your notes... Please wait ⏳</p>
            </div>
            """
            loader_placeholder.markdown(loader_html, unsafe_allow_html=True)

            with st.spinner("Summarizing your notes... Please wait ⏳"):
                text_parts = []
                gemini_files = []
                has_pdf = False

                # Include pasted text
                if text_content.strip():
                    text_parts.append(text_content.strip())

                # Handle uploaded files
                max_bytes = 10 * 1024 * 1024  # 10 MB per file limit
                for uploaded in uploaded_files or []:
                    suffix = Path(uploaded.name).suffix.lower()

                    # Enforce 10 MB limit for each uploaded file
                    if uploaded.size > max_bytes:
                        st.warning(
                            f"'{uploaded.name}' is larger than 10 MB. "
                            "Please upload a file less than 10 MB to proceed further."
                        )
                        continue

                    # Plain text files: read locally and append to text
                    if suffix == ".txt":
                        try:
                            file_text = uploaded.read().decode("utf-8", errors="ignore")
                            text_parts.append(file_text)
                        finally:
                            uploaded.seek(0)

                    # Word documents: extract text locally, do not upload to Gemini as files
                    elif suffix in [".doc", ".docx"]:
                        try:
                            file_bytes = uploaded.read()
                            doc_text = extract_text_from_docx(file_bytes)
                            if doc_text:
                                text_parts.append(doc_text)
                        except Exception as doc_err:
                            st.warning(f"Could not read Word document '{uploaded.name}': {doc_err}")
                        finally:
                            uploaded.seek(0)

                    # PowerPoint presentations: extract text locally
                    elif suffix in [".ppt", ".pptx"]:
                        try:
                            file_bytes = uploaded.read()
                            ppt_text = extract_text_from_pptx(file_bytes)
                            if ppt_text:
                                text_parts.append(ppt_text)
                        except Exception as ppt_err:
                            st.warning(f"Could not read PowerPoint file '{uploaded.name}': {ppt_err}")
                        finally:
                            uploaded.seek(0)

                    else:
                        # PDFs and images: upload to Gemini for multimodal summarization.
                        # On Windows, NamedTemporaryFile can cause permission issues because the
                        # file handle stays open. Instead, create a temp path, close the handle,
                        # then upload and finally delete the temp file.
                        if suffix == ".pdf":
                            has_pdf = True

                        fd, temp_path = tempfile.mkstemp(suffix=suffix)
                        os.close(fd)
                        try:
                            with open(temp_path, "wb") as tmp_file:
                                tmp_file.write(uploaded.getbuffer())

                            gemini_file = genai.upload_file(path=temp_path)
                            gemini_files.append(gemini_file)
                        finally:
                            try:
                                os.remove(temp_path)
                            except OSError:
                                # If deletion fails, just ignore; it will stay in OS temp dir.
                                pass

                combined_text = "\n\n".join(text_parts)

                try:
                    summary = summarize_notes(combined_text, gemini_files, selected_model, has_pdf)
                    if not summary:
                        st.error("Gemini returned an empty summary. Please try again.")
                    else:
                        st.session_state.summary = summary
                        st.success("✅ Summary generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error while generating summary: {e}")
                finally:
                    # Remove the overlay loader once done
                    loader_placeholder.empty()

    # Show the summary if available
    if st.session_state.summary:
        st.subheader("📚 Summarized Notes")
        st.markdown(st.session_state.summary)

    # Render footer
    render_footer()


if __name__ == "__main__":
    main()