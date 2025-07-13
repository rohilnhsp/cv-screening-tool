
import os
import re
import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

def check_password():
    def password_entered():
        if st.session_state["password"] == "cvsecure2024":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_fields(text):
    fields = {
        "Employment Status": re.search(r"(?i)(employment status)[:\-]?\s*(.+)", text),
        "GMC Registration": re.search(r"(?i)(GMC\s*(number|registration))[:\-]?\s*(.+)", text),
        "Specialties": re.search(r"(?i)(specialt(y|ies))[:\-]?\s*(.+)", text),
        "Grade Level": re.search(r"(?i)(grade level|current grade)[:\-]?\s*(.+)", text),
        "Postal Code": re.search(r"\b[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}\b", text),
        "Preferred Trust/Location": re.search(r"(?i)(prefer.*trust|prefer.*location)[:\-]?\s*(.+)", text),
        "Visa Status": re.search(r"(?i)(visa status)[:\-]?\s*(.+)", text),
        "NHS Experience": re.search(r"(?i)(NHS experience|worked in NHS)[:\-]?\s*(.+)", text),
        "DBS Status": re.search(r"(?i)(DBS status|current DBS)[:\-]?\s*(.+)", text),
        "BLS/ALS/MT": re.search(r"(?i)(BLS|ALS|manual handling).{0,50}", text),
        "Availability to Start": re.search(r"(?i)(available to start|availability)[:\-]?\s*(.+)", text),
        "Shift Availability": re.search(r"(?i)(available for|shift preference)[:\-]?\s*(.+)", text),
        "Expected Pay Rate": re.search(r"(?i)(expected pay rate|rate expected)[:\-]?\s*([$£]?\d+)", text),
    }

    result = {}
    for key, match in fields.items():
        if match:
            result[key] = match.group(len(match.groups()))
        else:
            result[key] = ""
    return result

if check_password():
    st.title("🧾 CV Screening Tool")
    st.write("Upload single or multiple CVs (PDF or DOCX). Fields will be auto-extracted and displayed below.")

    multiple = st.radio("How many CVs are you uploading?", ["Single", "Multiple"])
    uploaded_files = st.file_uploader("Upload CV(s):", type=["pdf", "docx"], accept_multiple_files=(multiple == "Multiple"))

    if uploaded_files:
        data = []
        
        files_to_process = uploaded_files if isinstance(uploaded_files, list) else [uploaded_files]
        
        for file in files_to_process:
            ext = os.path.splitext(file.name)[1].lower()
            if ext == ".pdf":
                text = extract_text_from_pdf(file)
            elif ext == ".docx":
                text = extract_text_from_docx(file)
            else:
                st.warning(f"Unsupported file format: {file.name}")
                continue

            extracted = extract_fields(text)
            extracted["File Name"] = file.name
            data.append(extracted)

        df = pd.DataFrame(data)
        st.success("✅ Extraction completed.")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", data=csv, file_name="cv_screening_results.csv", mime="text/csv")
