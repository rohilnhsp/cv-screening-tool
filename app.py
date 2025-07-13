import streamlit as st
import spacy
import re
from io import StringIO
from pdfminer.high_level import extract_text

# Load spaCy model once
@st.cache_resource
def load_spacy_model():
    return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

def extract_text_from_pdf(pdf_file):
    try:
        return extract_text(pdf_file)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def simple_keyword_search(text, keywords):
    """Return True if any keyword is found in text (case-insensitive)."""
    text = text.lower()
    for kw in keywords:
        if kw.lower() in text:
            return True
    return False

def extract_field(pattern, text, flags=0):
    """Extract first match from text using regex pattern."""
    match = re.search(pattern, text, flags)
    if match:
        return match.group(1).strip()
    return None

def main():
    st.title("📝 CV Screening Application")

    st.markdown(
        """
        Upload a CV (PDF or TXT) and this app will extract key details such as:
        - Current employment status
        - GMC registration details
        - Specialties
        - Visa status
        - NHS experience
        - DBS status
        - Training certifications (BLS/ALS)
        - Availability
        """
    )

    uploaded_file = st.file_uploader("Upload CV", type=["pdf", "txt"])

    if uploaded_file:
        # Extract text from uploaded file
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        else:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            text = stringio.read()

        st.subheader("Extracted Text Preview")
        st.write(text[:1000] + "..." if len(text) > 1000 else text)

        # Lowercase text for keyword matching
        text_lower = text.lower()

        st.subheader("Extracted Information")

        # Current employment status (look for keywords)
        employment_keywords = ["currently employed", "unemployed", "on leave", "working as", "self-employed"]
        employment_status = "Unknown"
        for kw in employment_keywords:
            if kw in text_lower:
                employment_status = kw.capitalize()
                break
        st.write(f"**Employment Status:** {employment_status}")

        # GMC Registration number (usually a 7 digit number)
        gmc_pattern = r"(GMC\s*Number|GMC\s*Reg(?:istration)?\s*No\.?:?)\s*([0-9]{6,8})"
        gmc = extract_field(gmc_pattern, text, flags=re.I)
        st.write(f"**GMC Registration:** {gmc if gmc else 'Not found'}")

        # Specialties (try to find some common specialties)
        specialties = ["General Practice", "Psychiatry", "Paediatrics", "Emergency Medicine", "Anaesthetics", "Surgery", "Radiology"]
        found_specialties = [spec for spec in specialties if spec.lower() in text_lower]
        st.write(f"**Specialties:** {', '.join(found_specialties) if found_specialties else 'Not found'}")

        # Visa status
        visa_keywords = ["british citizen", "indefinite leave to remain", "tier 2 visa", "work permit", "student visa"]
        visa_status = next((kw for kw in visa_keywords if kw in text_lower), "Not found")
        st.write(f"**Visa Status:** {visa_status}")

        # NHS Experience (look for 'NHS' + years or phrases)
        nhs_exp_pattern = r"NHS\s*(?:experience|worked|for)\s*(\d+)\s*(?:years|yrs)?"
        nhs_exp = extract_field(nhs_exp_pattern, text, flags=re.I)
        st.write(f"**NHS Experience (years):** {nhs_exp if nhs_exp else 'Not found'}")

        # DBS status (Disclosure and Barring Service)
        dbs_keywords = ["dbs cleared", "dbs certificate", "dbs check", "dbs pending"]
        dbs_status = next((kw for kw in dbs_keywords if kw in text_lower), "Not found")
        st.write(f"**DBS Status:** {dbs_status}")

        # Training (BLS / ALS)
        bls_keywords = ["bls certified", "basic life support", "bls training"]
        als_keywords = ["als certified", "advanced life support", "als training"]
        bls_status = next((kw for kw in bls_keywords if kw in text_lower), "Not found")
        als_status = next((kw for kw in als_keywords if kw in text_lower), "Not found")
        st.write(f"**BLS Training:** {bls_status}")
        st.write(f"**ALS Training:** {als_status}")

        # Availability (basic)
        availability_keywords = ["full-time", "part-time", "ad hoc", "weekends", "immediate start"]
        availability = [kw for kw in availability_keywords if kw in text_lower]
        st.write(f"**Availability:** {', '.join(availability) if availability else 'Not found'}")

if __name__ == "__main__":
    main()
