# main_app.py
import os
import streamlit as st
import pdfplumber
from docx import Document as docx_document
from learning_roadmap import generate_learning_roadmap
from project_recommendations import suggest_projects
from resume_analysis import evaluate_resume_profile
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import plotly.graph_objects as go

# Load OpenAI key
openai_api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------
# Helper Functions
# -----------------------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = docx_document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# -----------------------------
# Upload Page
# -----------------------------
def show_upload_page(user_id=None):
    st.title("Welcome to SkillMentor AI!")

    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    if not uploaded_file:
        st.info("Please upload your resume to continue.")
        return

    # Extract resume text
    resume_text = ""
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = extract_text_from_docx(uploaded_file)
    st.session_state["resume_text"] = resume_text

    # User Inputs
    interests = st.multiselect("Select your interests:",
                               ["Artificial Intelligence", "Web Development", "Data Science",
                                "Cybersecurity", "Cloud Computing", "Mobile App Development",
                                "Game Development", "UI/UX Design", "Software Developer"])
    st.session_state["interests"] = interests

    career_goal_known = st.checkbox("I know my career goal")
    if career_goal_known:
        career_goal = st.selectbox("Select your career goal:",
                                   ["Data Scientist", "Software Engineer", "Cybersecurity Analyst",
                                    "Cloud Architect", "Mobile App Developer","Frontend Developer"])
        st.session_state['career_goal'] = career_goal
    else:
        st.info("Based on your resume and interests, we will suggest a suitable role.")
        if st.button("Suggest me a career goal"):
            llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key, temperature=0)
            prompt = f"""
You are an expert career coach.

Resume:
{resume_text}

User Interests: {', '.join(interests)}

Task:
Suggest one suitable career goal/job role for this user based on the resume and interests. 
Return ONLY the job title as plain text.
"""
            response = llm([HumanMessage(content=prompt)])
            if isinstance(response, list):
                suggested_goal = response[0].content.strip()
            elif hasattr(response, "content"):
                suggested_goal = response.content.strip()
            else:
                suggested_goal = str(response).strip()
            st.session_state['career_goal'] = suggested_goal
            st.success(f"Suggested Career Goal: {suggested_goal}")

    # Start Analysis
    if "career_goal" in st.session_state and st.button("Start Analysis"):
        st.session_state["current_page"] = "dashboard"
        with st.spinner("Analyzing resume and computing skill match..."):
            analysis_result = evaluate_resume_profile(
                st.session_state["resume_text"],
                st.session_state["interests"],
                st.session_state["career_goal"]
            )
            st.session_state["analysis_result"] = analysis_result
            st.session_state["resume_uploaded"] = True

# Dashboard Page
def show_dashboard_page():
    st.title("Resume Analysis Dashboard 📊")
    analysis_result = st.session_state.get("analysis_result")
    career_goal = st.session_state.get("career_goal")
    resume_uploaded = st.session_state.get("resume_uploaded", False)

    if not analysis_result or not resume_uploaded:
        st.warning("No analysis data found. Please upload your resume and start analysis first.")
        return

    # Tabs
    tabs = st.tabs(["Profile Summary", "Skill Match & Gap", "Recommendations", "Learning Roadmap", "Project Recommendations"])

    # Profile Summary Tab
    with tabs[0]:
        st.subheader("Profile Summary")
        extracted_skills = analysis_result.get("extracted_skills", [])
        required_skills = analysis_result.get("required_skills", [])
        st.write(f"**Extracted Skills:** {', '.join(extracted_skills)}")
        st.write(f"**Required Skills:** {', '.join(required_skills)}")

    # ----- Skill Match & Gap Tab -----
    with tabs[1]:
        st.subheader("Skill Match & Gap")
        skill_match = analysis_result.get("skill_match_percentage", 0)
        skill_gap = analysis_result.get("skill_gap_percentage", 0)
        st.metric("Skill Match %", f"{skill_match}%")
        st.metric("Skill Gap %", f"{skill_gap}%")
        missing_skills = analysis_result.get("missing_skills", [])
        if missing_skills:
            st.write("**Missing Skills:**", ", ".join(missing_skills))
        else:
            st.write("No skills missing!")
              # Visualization: Donut Chart
        labels = ['Skills Acquired', 'Skills Missing']
        values = [skill_match, skill_gap]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=['#00cc96', '#ef553b']))])
        fig.update_layout(title_text="Skill Match vs Skill Gap", title_font_size=20)
        st.plotly_chart(fig, use_container_width=True)

    # ----- Recommendations Tab -----
    with tabs[2]:
        st.subheader("Recommendations to Bridge Gaps")
        for rec in analysis_result.get("recommendations", []):
            with st.expander(rec[:30]+"..."):
                st.write(rec)

    # ----- Learning Roadmap Tab -----
    with tabs[3]:
        st.subheader("Learning Roadmap to Bridge Skill Gaps")
        roadmap = generate_learning_roadmap(missing_skills)
        for i, item in enumerate(roadmap):
            if isinstance(item, dict):
                with st.expander(item.get("skill", f"Skill {i+1}")):
                    st.write(f"**Course:** {item.get('recommended_course')}")
                    st.write(f"**Platform:** {item.get('platform')}")
                    st.write(f"**Estimated Duration:** {item.get('estimated_duration')}")
            else:
                st.write(item)

    # ----- Project Recommendations Tab -----
    with tabs[4]:
        st.session_state["want_projects"] = st.checkbox(
            "Show project recommendations?", value=st.session_state.get("want_projects", False)
        )
        if st.session_state["want_projects"] and career_goal:
            projects = suggest_projects(career_goal)
            for i, proj in enumerate(projects):
                if isinstance(proj, dict):
                    with st.expander(proj.get("project_name", f"Project {i+1}")):
                        st.write(f"**Description:** {proj.get('description')}")
                        st.write(f"**Estimated Duration:** {proj.get('estimated_duration')}")
                else:
                    st.write(proj)

# -----------------------------
# Main App Content
# -----------------------------
def main_app_content(logout_callback, user_id=None):
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "upload"

    if st.session_state["current_page"] == "upload":
        show_upload_page(user_id)
    elif st.session_state["current_page"] == "dashboard":
        show_dashboard_page()

    # Sidebar Logout and "Upload New Resume" button
    st.sidebar.header("Navigation")
    if st.sidebar.button("Upload New Resume / Start Fresh Analysis"):
        st.session_state["current_page"] = "upload"
        st.session_state["resume_uploaded"] = False
        st.session_state["analysis_result"] = None
        st.session_state["resume_text"] = None
        st.session_state["interests"] = None
        st.session_state["career_goal"] = None
        st.session_state["want_projects"] = False

    if st.sidebar.button("Logout"):
        logout_callback()
