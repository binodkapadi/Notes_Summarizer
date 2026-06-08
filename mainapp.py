import os
import tempfile
from io import BytesIO
from pathlib import Path

import google.generativeai as genai
import streamlit as st
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
from docx import Document
from dotenv import load_dotenv
from fpdf import FPDF
from markdown import markdown
from pptx import Presentation

# Load environment variables
load_dotenv()

# Configure Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Mapping between human‑friendly names and Gemini model IDs
MODEL_OPTIONS = {
    "Gemini Flash-Lite Latest": "gemini-flash-lite-latest",
    "Gemini Flash Latest": "gemini-flash-latest",
    "Gemini 2.5 Flash-Lite Preview": "gemini-2.5-flash-lite-preview-09-2025",
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Flash-Lite": "gemini-2.5-flash-lite",
}

FONT_CANDIDATES = [
    (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
    ),
    (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ),
    (
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ),
    (
        Path("assets/fonts/DejaVuSans.ttf"),
        Path("assets/fonts/DejaVuSans-Bold.ttf"),
    ),
]


def locate_font_paths() -> tuple[Path, Path]:
    """Return paths to regular and bold font files that support Unicode."""
    for regular, bold in FONT_CANDIDATES:
        if regular.exists():
            bold_path = bold if bold and bold.exists() else regular
            return regular, bold_path
    raise FileNotFoundError(
        "Could not locate a Unicode font. Please add a TTF font (e.g. DejaVuSans) "
        "under assets/fonts/ or update FONT_CANDIDATES with the correct paths."
    )


def summarize_notes(all_text: str, gemini_files, model_name: str, has_pdf: bool) -> str:
    """
    Call Gemini to create thorough, human-friendly study notes from text + uploaded files.
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


def generate_summary_pdf(summary_markdown: str) -> bytes:
    """Convert the summary markdown to a mobile-friendly PDF with UI-like spacing."""
    font_regular, font_bold = locate_font_paths()

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.add_font("Body", "", str(font_regular), uni=True)
    pdf.add_font("BodyBold", "", str(font_bold), uni=True)

    html = markdown(summary_markdown, extensions=["tables"])
    soup = BeautifulSoup(html, "html.parser")

    def add_spacing(lines: int = 4):
        pdf.ln(lines)

    def line_count(text: str, width: float) -> int:
        """Estimate line count for table cells."""
        words = (text or "").split()
        if not words:
            return 1
        lines = 1
        current = ""
        for word in words:
            tentative = (current + " " if current else "") + word
            if pdf.get_string_width(tentative) > width:
                lines += 1
                current = word
            else:
                current = tentative
        return lines

    first_block = True

    for block in soup.children:
        if not getattr(block, "name", None):
            continue

        tag = block.name.lower()
        text = block.get_text(" ", strip=True)

        if tag in {"h1", "h2", "h3", "h4"}:
            if not first_block:
                add_spacing(6)
            font_sizes = {"h1": 20, "h2": 17, "h3": 15, "h4": 13}
            heading_colors = {
                "h1": (34, 99, 188),
                "h2": (52, 152, 219),
                "h3": (44, 62, 80),
                "h4": (44, 62, 80),
            }
            pdf.set_text_color(*heading_colors.get(tag, (0, 0, 0)))
            pdf.set_font("BodyBold", size=font_sizes.get(tag, 14))
            pdf.multi_cell(0, 8, text)
            pdf.set_text_color(0, 0, 0)
            add_spacing(4)
        elif tag == "p" and text:
            pdf.set_font("Body", size=11)
            pdf.multi_cell(0, 6, text)
            add_spacing(4)
        elif tag in {"ul", "ol"}:
            items = [
                li.get_text(" ", strip=True)
                for li in block.find_all("li", recursive=False)
            ]
            pdf.set_font("Body", size=11)
            add_spacing(2)
            for idx, item in enumerate(items, start=1):
                bullet = "-" if tag == "ul" else f"{idx}."
                pdf.multi_cell(0, 6, f"{bullet} {item}")
            add_spacing(4)
        elif tag == "table":
            add_spacing(4)
            rows = []
            max_cols = 0
            for tr in block.find_all("tr"):
                cells = tr.find_all(["th", "td"])
                row_texts = [c.get_text(" ", strip=True) for c in cells]
                rows.append(row_texts)
                max_cols = max(max_cols, len(row_texts))

            if not rows or max_cols == 0:
                continue

            content_width = pdf.w - pdf.l_margin - pdf.r_margin
            col_width = content_width / max_cols
            line_height = 7

            for idx, row in enumerate(rows):
                normalized = row + [""] * (max_cols - len(row))
                is_header = idx == 0
                pdf.set_font("BodyBold" if is_header else "Body", size=11)
                pdf.set_fill_color(28, 42, 62) if is_header else pdf.set_fill_color(250, 250, 250)
                pdf.set_text_color(255, 255, 255) if is_header else pdf.set_text_color(0, 0, 0)

                start_x = pdf.get_x()
                start_y = pdf.get_y()
                max_lines = 1

                for col_idx, cell_text in enumerate(normalized):
                    lines = max(line_count(cell_text, col_width - 2), 1)
                    max_lines = max(max_lines, lines)
                    pdf.multi_cell(
                        col_width,
                        line_height,
                        cell_text,
                        border=1,
                        align="L",
                        fill=True,
                    )
                    pdf.set_xy(start_x + col_width * (col_idx + 1), start_y)

                pdf.set_xy(start_x, start_y + max_lines * line_height)
                pdf.set_text_color(0, 0, 0)
            add_spacing(6)
        elif tag == "hr":
            pdf.set_draw_color(200, 200, 200)
            y = pdf.get_y()
            pdf.line(10, y, 200, y)
            add_spacing(4)

        first_block = False

    # FPDF returns latin-1 encoded str; ensure bytes output
    pdf_str = pdf.output(dest="S")
    return pdf_str.encode("latin-1", "ignore")


def main():
    st.title("📝 Notes Summarizer")

    # Optional dark mode CSS (force UTF-8 to avoid Windows cp1252 decode errors)
    if os.path.exists("style.css"):
        with open("style.css", "r", encoding="utf-8", errors="ignore") as f:
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
    uploaded_file = st.file_uploader(
        "📂 Or upload notes as PDF, Word, PPT, text, or images (limit 50MB per file):",
        type=["pdf", "doc", "docx", "ppt", "pptx", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=False,
        help="Limit 50MB per file • Supports PDF, DOC/DOCX, PPT/PPTX, TXT, PNG, JPG.",
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
        if not text_content.strip() and not uploaded_file:
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
                max_bytes = 50 * 1024 * 1024  # 50 MB per file limit
                uploads_to_process = [uploaded_file] if uploaded_file else []
                for uploaded in uploads_to_process:
                    suffix = Path(uploaded.name).suffix.lower()

                    # Enforce 50 MB limit for each uploaded file
                    if uploaded.size > max_bytes:
                        st.warning(
                            f"'{uploaded.name}' is larger than 50 MB. "
                            "Please upload a file less than 50 MB to proceed further."
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

        # Print / Save as PDF using browser (exact visual copy)
        if st.button("🖨️ Print / Save as PDF", key="print_summary"):
            # Open a minimal HTML document containing only the summarized notes,
            # then trigger the browser print dialog. This keeps formatting very
            # close to what is shown in the app while giving the browser full
            # control over PDF generation.
            summary_html = markdown(st.session_state.summary, extensions=["tables"])
            printable_html = f"""
            <html>
              <head>
                <meta charset="utf-8" />
                <title>Summarized Notes</title>
                <style>
                  /* Screen styles */
                  body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    padding: 24px;
                    background-color: #020617;
                    color: #e5e7eb;
                  }}
                  h1, h2, h3, h4 {{
                    color: #60a5fa;
                    margin-top: 1.4rem;
                    margin-bottom: 0.6rem;
                  }}
                  p {{
                    margin: 0.4rem 0;
                    line-height: 1.5;
                  }}
                  ul, ol {{
                    margin: 0.4rem 0 0.8rem 1.5rem;
                  }}
                  table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1rem 0;
                  }}
                  th, td {{
                    border: 1px solid #4b5563;
                    padding: 0.4rem 0.6rem;
                  }}
                  th {{
                    background-color: #111827;
                  }}
                  
                  /* Print/PDF styles - Remove headers, footers, and overlays */
                  @media print {{
                    @page {{
                      margin: 0.75in;
                      size: auto;
                    }}
                    
                    /* Remove all browser default headers and footers */
                    @page {{
                      margin-top: 0.5in;
                      margin-bottom: 0.5in;
                    }}
                    
                    /* Hide any overlays or loaders */
                    .overlay-loader,
                    .overlay-loader-circle,
                    .overlay-loader-text,
                    header,
                    footer {{
                      display: none !important;
                      visibility: hidden !important;
                    }}
                    
                    /* Remove blur effects */
                    * {{
                      backdrop-filter: none !important;
                      -webkit-backdrop-filter: none !important;
                      filter: none !important;
                      -webkit-filter: none !important;
                    }}
                    
                    /* Clear, readable content */
                    body {{
                      background: white !important;
                      color: #000000 !important;
                      padding: 0 !important;
                      -webkit-print-color-adjust: exact;
                      print-color-adjust: exact;
                    }}
                    
                    /* Black text for better readability */
                    h1, h2, h3, h4, h5, h6 {{
                      color: #000000 !important;
                      page-break-after: avoid;
                    }}
                    
                    p, li, td, th, span, div {{
                      color: #000000 !important;
                    }}
                    
                    /* Remove shadows that might cause blur */
                    * {{
                      box-shadow: none !important;
                      text-shadow: none !important;
                    }}
                    
                    /* Ensure tables print well */
                    table {{
                      border-collapse: collapse;
                      page-break-inside: avoid;
                    }}
                    
                    th, td {{
                      border: 1px solid #000000 !important;
                      padding: 0.4rem 0.6rem;
                    }}
                    
                    th {{
                      background-color: #f0f0f0 !important;
                      color: #000000 !important;
                    }}
                  }}
                </style>
              </head>
              <body>
                {summary_html}
                <script>
                  window.onload = function() {{ window.print(); }};
                </script>
              </body>
            </html>
            """
            components.html(printable_html, height=0, width=0)

    # Render footer
    render_footer()


if __name__ == "__main__":
    main()