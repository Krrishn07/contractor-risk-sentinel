from pypdf import PdfReader

def extract_text_from_file(uploaded_file):
    """Handles PDF and Text file extraction safely."""
    try:
        if uploaded_file.name.endswith(".pdf"):
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages: 
                text += page.extract_text() or ""
            return text
        else:
            uploaded_file.seek(0)
            return uploaded_file.read().decode("utf-8")
    except Exception as e:
        return None