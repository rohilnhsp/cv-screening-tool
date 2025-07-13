import streamlit as st
import re
import spacy
import pdfplumber
import docx
from io import BytesIO

@st.cache_resource
def load_spacy():
    return spacy.load("en_core_web_sm")

nlp = load_spacy()

def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_bytes):
    doc = docx.Document(BytesIO(file_bytes))
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return "\n".join(fullText)

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.type
    file_bytes = uploaded_file.read()
    if file_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        # For .docx supported only
        try:
            return extract_text_from_docx(file_bytes)
        except Exception as e:
            return ""
    elif file_type == "text/plain":
        return file_bytes.decode("utf-8")
    else:
        return ""

def extract_basic_info(text):
    info = {}

    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    info["Emails"] = emails[0] if emails else "N/A"

    phones = re.findall(r"\+?\d[\d \-\(\)]{7,}\d", text)
    info["Phone"] = phones[0] if phones else "N/A"

    specialties = []
    keywords = ["MBBS", "MD", "GP", "Psychiatry", "Surgery", "Anaesthesia", "Emergency Medicine"]
    for kw in keywords:
        if kw.lower() in text.lower():
            specialties.append(kw)
    info["Specialties"] = ", ".join(specialties) if specialties else "N/A"

    return info

def extract_with_spacy(text):
    doc = nlp(text)
    ents = [(ent.text, ent.label_) for ent in doc.ents]
    return ents

st.title("📝 CV Screening with PDF & DOCX Upload")

uploaded_file = st.file_uploader(
    "Upload your CV (PDF, DOCX, or TXT)",
    type=["pdf", "docx", "txt"],
    help="Supports PDF, DOCX, and plain text files."
)

if uploaded_file:
    with st.spinner("Extracting text..."):
        text = extract_text_from_file(uploaded_file)
    if not text.strip():
        st.error("Could not extract text from the uploaded file.")
    else:
        st.subheader("Extracted Basic Info:")
        basic_info = extract_basic_info(text)
        st.json(basic_info)

        st.subheader("Named Entities from spaCy:")
        ents = extract_with_spacy(text)
        st.write(ents)
else:
    st.info("Please upload a CV file to start extraction.")
