import streamlit as st
from llm import generate_jd, generate_faqs, DEFAULT_TEMPERATURE


st.set_page_config(page_title="AI Job Description Generator", layout="wide")

LANGUAGES = [
    "English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam",
    "Marathi", "Gujarati", "Bengali", "Punjabi", "Odia"
]

st.title("AI Job Description Generator")
st.caption("Generate Reliance Jio–branded Job Descriptions and Interview FAQs with AI")


if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "faqs_text" not in st.session_state:
    st.session_state.faqs_text = ""
if "last_job_key" not in st.session_state:
    st.session_state.last_job_key = None

# ---- LAYOUT ----
col_input, col_jd, col_faq = st.columns([2, 5.5, 3.5])

# ---- COLUMN 1: INPUT FORM ----
with col_input:
    st.subheader("Job Details")
    job_title = st.text_input("Job Title", placeholder="e.g., HR Head")
    industry = st.selectbox("Function", [
        "Apprentice", "Business Operations", "Corporate Services (Admin)", "Customer Service",
        "Engineering and Technology", "Finance Compliance & Accounting", "Freelancer - Sales Associate",
        "Freelancer", "Freelancer Enterprise", "Human Resources & Training", "Infrastructure",
        "Information Security", "IT & Systems", "Jio Sales Associate", "Legal", "Marketing",
        "Operations", "Others", "Procurement and Contracts", "Product Management", "Regulatory",
        "Sales and Distribution", "Supply Chain"
    ])
    experience = st.selectbox("Experience Required", [
        "Fresher", "Junior: 1-3 years", "Mid-Level: 4-6 years",
        "Senior: 7-10 years", "Executive: More than 10 years"
    ])
    skills = st.text_area("Skills", placeholder="e.g., Communication, Negotiation, Team player")

    temperature = st.slider(
        "Creativity (Temperature)", 0.0, 1.0, DEFAULT_TEMPERATURE, 0.1
    )
    language = st.selectbox("Language", LANGUAGES, index=0)

    generate_btn = st.button("Generate JD & FAQs", use_container_width=True)

# ---- COLUMN 2: JOB DESCRIPTION OUTPUT ----
with col_jd:
    st.subheader("Generated Job Description")
    jd_output = st.empty()

# ---- COLUMN 3: INTERVIEW FAQ OUTPUT ----
with col_faq:
    st.subheader("Interview FAQs")
    faq_output = st.empty()


# ---- CACHE FAQ GENERATION ----
@st.cache_data(show_spinner=False)
def cached_generate_faq(job_title, industry, experience):
    """Generate FAQs once per job combination (language-agnostic)."""
    return generate_faqs(
        job_title=job_title,
        industry=industry,
        experience=experience,
        language="English",  # Keep FAQs in base language
        temperature=0.7,
    )


# ---- GENERATION LOGIC ----
def generate_all():
    if not job_title or not industry or not experience:
        jd_output.warning("Please fill all required fields.")
        faq_output.warning("Please fill all required fields.")
        return

    # Create a unique key for the *job*, not language
    job_key = f"{job_title}_{industry}_{experience}"

    # --- Generate JD (always language-dependent) ---
    with st.spinner(f"Generating Job Description in {language}..."):
        try:
            jd_text = generate_jd(
                job_title=job_title,
                industry=industry,
                experience=experience,
                skills=skills,
                temperature=temperature,
                language=language,
            )
            st.session_state.jd_text = jd_text
            jd_output.markdown("---\n" + jd_text)
        except Exception as e:
            jd_output.error(f"Failed to generate JD. Error: {str(e)}")
            return

    # --- Generate FAQs only once per job ---
    if st.session_state.last_job_key != job_key:
        with st.spinner("Generating Interview FAQs..."):
            try:
                faqs_text = cached_generate_faq(job_title, industry, experience)
                st.session_state.faqs_text = faqs_text
                st.session_state.last_job_key = job_key
                faq_output.markdown("---\n" + faqs_text)
            except Exception as e:
                faq_output.error(f"Failed to generate FAQs. Error: {str(e)}")
    else:
        # Just reuse cached FAQs (don’t regenerate)
        faq_output.markdown("---\n" + st.session_state.faqs_text)


# ---- TRIGGER ----
if generate_btn:
    generate_all()

# ---- RE-RENDER EXISTING STATE (on reruns) ----
if st.session_state.jd_text:
    jd_output.markdown("---\n" + st.session_state.jd_text)
if st.session_state.faqs_text:
    faq_output.markdown("---\n" + st.session_state.faqs_text)

