import streamlit as st
from openai import OpenAI
import PyPDF2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the page layout
st.set_page_config(page_title="AI Resume & Cover Letter Generator", layout="wide")

st.title("📄 AI Resume & Cover Letter Generator")
st.markdown("Generate ATS-optimized resumes and cover letters using the system prompt rules you provided!")

# Automatically configure OpenRouter API from environment variable
api_key = os.getenv("OPENROUTER_API_KEY")
client = None
if api_key:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
else:
    st.sidebar.error("⚠️ OPENROUTER_API_KEY not found in environment variables or .env file.")

# --- NEW APP MODE SELECTION ---
st.sidebar.header("🕹️ Mode Selection")
app_mode = st.sidebar.radio("What would you like to do?", ["🎯 Targeted RAG Generator", "✨ Improve Existing Resume"])

def get_user_profile():
    profile_input_type = st.radio("How would you like to provide your profile/resume?", ["Text", "Upload PDF"])
    user_profile = ""
    if profile_input_type == "Text":
        user_profile = st.text_area("Paste your resume or profile details here:", height=250)
    else:
        uploaded_file = st.file_uploader("Upload your Resume/CV (PDF)", type=["pdf"])
        if uploaded_file is not None:
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    user_profile += page.extract_text() + "\n"
                st.success("PDF uploaded and parsed successfully!")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")
    return user_profile

def call_ai(prompt_text):
    """Helper function to call OpenRouter API"""
    completion = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[
            {
                "role": "user",
                "content": prompt_text
            }
        ]
    )
    return completion.choices[0].message.content

if app_mode == "🎯 Targeted RAG Generator":
    # Layout for Inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Your Profile / Resume")
        user_profile = get_user_profile()
            
    with col2:
        st.subheader("2. Target Job Description")
        job_description = st.text_area("Paste the target Job Description here:", height=325)

    st.markdown("---")

    # Generation Button
    if st.button("🚀 Generate Resume & Cover Letter", use_container_width=True):
        if not api_key:
            st.error("⚠️ API Key is missing. Please set OPENROUTER_API_KEY in your .env file or environment variables.")
        elif not user_profile or not job_description:
            st.error("⚠️ Please provide both your Profile and the Job Description.")
        else:
            with st.spinner("Extracting key information (Step 1)..."):
                try:
                    # Step 1: Extraction using the new prompt
                    extraction_prompt = f"""Given:

User Profile:
{user_profile}

Job Description:
{job_description}

Find and return only useful information for resume making:

Focus on:
- Matching skills
- Relevant projects
- Important keywords from job

Return only important data, no extra text."""
                    
                    extracted_info = call_ai(extraction_prompt)
                    
                except Exception as e:
                    st.error(f"An error occurred during extraction: {e}")
                    extracted_info = ""

            if extracted_info:
                with st.spinner("Improving Project Bullet Points..."):
                    try:
                        project_prompt = f"""Improve these project descriptions:

{extracted_info}

Make them:
- Strong
- Use action words
- Add numbers/results
- Match job role: {job_description}

Return better bullet points."""
                        improved_projects = call_ai(project_prompt)
                    except Exception as e:
                        improved_projects = "Error improving projects."

                with st.spinner("Generating Final Documents (Step 2)..."):
                    try:
                        # Step 2: Final Generation using your exact updated prompt
                        prompt = f"""Use the data below:

[PROFILE]
{user_profile}

[JOB DESCRIPTION]
{job_description}

[CONTEXT]
Extracted Information:
{extracted_info}

Improved Projects:
{improved_projects}

Do 3 things:

-------------------------------------

1. RESUME

Create a clean resume:

- Name + Contact
- Summary (2-3 lines)
- Skills (job matching)
- Projects / Experience (bullet points + action words + impact)
- Education
- Extra (if available)

-------------------------------------

2. COVER LETTER

Write a simple cover letter:

- Start with role
- Explain why I am a good fit
- Mention skills/projects
- End confidently

(Keep under 250-300 words)

-------------------------------------

3. ATS CHECK

From the job description:
- Extract important keywords (skills, tools, tech)

Compare with user profile:
- Which keywords match
- Which are missing

Give:
- Match %
- Suggestions to improve resume

-------------------------------------

FINAL OUTPUT FORMAT:

=== RESUME ===
(write here)

=== COVER LETTER ===
(write here)

=== ATS CHECK ===
Match %:
Matching keywords:
Missing keywords:
Suggestions:

-------------------------------------

Keep everything simple and professional."""
                        response_text = call_ai(prompt)
                        
                        st.success("✨ Generation Complete!")
                        
                        # Display output safely using tabs
                        tab1, tab2, tab3 = st.tabs(["📝 Final Documents & ATS", "🔍 Extracted Info (RAG)", "🚀 Improved Projects"])
                        
                        with tab1:
                            st.markdown(response_text)
                            
                        with tab2:
                            st.markdown("### Extracted Useful Information")
                            st.markdown("This information was extracted in Step 1 to ground the AI and prevent hallucination:")
                            st.markdown(extracted_info)
                            
                        with tab3:
                            st.markdown("### 🚀 Supercharged Project Bullet Points")
                            st.markdown("These bullet points have been optimized with strong action words and metrics:")
                            st.markdown(improved_projects)
                            
                    except Exception as e:
                        st.error(f"An error occurred while generating documents: {e}")

else:
    # Mode 2: Improve Existing Resume
    st.subheader("1. Your Current Resume")
    user_profile = get_user_profile()
    
    st.markdown("---")
    
    if st.button("✨ Supercharge Resume", use_container_width=True):
        if not api_key:
            st.error("⚠️ API Key is missing. Please set OPENROUTER_API_KEY in your .env file or environment variables.")
        elif not user_profile:
            st.error("⚠️ Please provide your Resume.")
        else:
            with st.spinner("Analyzing and Improving Resume..."):
                try:
                    prompt = f"""Check this resume:

{user_profile}

Please do two things:

1. ATS ANALYSIS:
- Give a general ATS friendliness score out of 100 (based on standard formatting, action verbs, and clarity).
- List 3 quick suggestions to improve the current resume.

2. IMPROVED RESUME:
Rewrite the resume to be highly ATS-friendly:
- Better wording
- Strong action words
- Add quantifiable impact

Output exactly in this format:

### 📊 Current ATS Analysis
**Score:** [Score]/100
**Suggestions:**
- [Suggestion 1]
- [Suggestion 2]
- [Suggestion 3]

---

### 🚀 Improved ATS-Friendly Resume
[Write the improved resume here]"""
                    
                    response_text = call_ai(prompt)
                    
                    st.success("✨ Improvement Complete!")
                    st.markdown("### 🚀 Improved Resume")
                    st.markdown(response_text)
                    
                except Exception as e:
                    st.error(f"An error occurred while generating documents: {e}")
