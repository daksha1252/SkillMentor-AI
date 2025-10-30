# resume_analysis.py
import os
import re
import json
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# Load OpenAI key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

def evaluate_resume_profile(resume_text, interests, career_goal):
    """
    GPT-powered resume analysis:
    - Extract skills dynamically from the resume (technical + internships + projects + experience)
    - Determine required skills for selected interests & career goal
    - Compute skill match % and skill gap %
    - Provide actionable recommendations
    """
    llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key, temperature=0)

    prompt = f"""
You are an expert career coach.

Resume:
{resume_text}

User Interests: {', '.join(interests)}
Career Goal: {career_goal}

Tasks:
1. Extract all skills mentioned anywhere in the resume, including:
   - Technical skills
   - Internships
   - Projects
   - Work experience
   - Achievements
2. List all the skills required for the selected interests and career goal.
3. Compute skill match percentage (skills they have / skills required).
4. Compute skill gap percentage.
5. List missing skills.
6. Provide 3-5 actionable recommendations (courses, learning paths, or projects) to cover missing skills.

**Important:** Return ONLY JSON, no extra text. The JSON keys must be:
- extracted_skills
- required_skills
- skill_match_percentage
- skill_gap_percentage
- missing_skills
- recommendations
"""

    # Call GPT
    response = llm([HumanMessage(content=prompt)])

    # Extract text from GPT response
    if isinstance(response, list) and len(response) > 0:
        response_text = response[0].content
    elif hasattr(response, "content"):
        response_text = response.content
    else:
        response_text = str(response)

    # Clean JSON inside any markdown fences
    response_text = re.sub(r"```(?:json)?", "", response_text).replace("```", "").strip()
    response_text = response_text.replace("'", '"')  # ensure proper JSON quotes

    # Parse JSON safely
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {"extracted_skills": [], "required_skills": [], "skill_match_percentage": 0,
                  "skill_gap_percentage": 0, "missing_skills": [], "recommendations": []}

    # Ensure all keys exist
    keys = ["extracted_skills", "required_skills", "skill_match_percentage",
            "skill_gap_percentage", "missing_skills", "recommendations"]
    for k in keys:
        if k not in result:
            result[k] = [] if "skills" in k or k=="recommendations" else 0

    return result
