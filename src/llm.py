import os
import toml
import yaml
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Load config ---
config = toml.load("config.toml")
os.environ["GOOGLE_API_KEY"] = config["google"]["api_key"]

DEFAULT_TEMPERATURE = 0.7

# --- Load JD prompt ---
def load_prompt():
    with open("src/prompt.yaml", "r") as pmp:
        data = yaml.safe_load(pmp)
    return ChatPromptTemplate.from_template(data["template"])

# --- Generate Job Description ---
def generate_jd(job_title, industry, experience, skills, language="English", temperature=DEFAULT_TEMPERATURE):
    """
    Generate a professional Job Description for Reliance Jio
    directly in the selected language using Gemini.
    """
    prompt = load_prompt()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=temperature)
    chain = prompt | llm

    inputs = {
        "job_title": job_title,
        "industry": industry,
        "experience": experience,
        "skills": skills,
        "language": language
    }

    print("Using API Key:", os.environ["GOOGLE_API_KEY"][:8] + "****")
    print("Temperature:", temperature)
    print("Inputs:", inputs)

    response = chain.invoke(inputs)
    return response.content

# --- Generate Interview FAQs ---
def generate_faqs(job_title, industry, experience, language="English", temperature=DEFAULT_TEMPERATURE):
    """
    Generate the most frequently asked interview questions for a role
    using Gemini, directly in the selected language.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=temperature)

    faq_prompt = f"""
    You are an expert HR interviewer with experience conducting interviews for {industry} roles.
    Your task is to generate the most frequently asked and most relevant interview questions
    for the following role at Reliance Jio.

    - Job Title: {job_title}
    - Industry: {industry}
    - Experience Level: {experience}
    
    provide questions in bullet form with numbering and just provide question trim all the alternative part

    Requirements:
    - Generate the output in {language}.
    - Focus on practical, high-impact questions that recruiters and hiring managers actually ask.
    - Cover both technical and behavioral aspects.
    - Return 8-12 questions in bullet point format.
    - Keep them concise and professional.
    """

    response = llm.invoke(faq_prompt)
    return response.content
