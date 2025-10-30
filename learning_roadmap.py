import os
import json
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def generate_learning_roadmap(missing_skills):
    """
    Generate a structured learning roadmap for missing skills using GPT-4o.
    Handles GPT responses wrapped inside a "text" field.
    Returns a list of dicts: skill, recommended_course, platform, estimated_duration.
    """
    if not missing_skills:
        return [{"message": "No missing skills detected. No roadmap needed."}]

    prompt = f"""
You are a career coach.

The user is missing the following skills: {', '.join(missing_skills)}

Tasks:
1. Generate a structured learning roadmap to bridge these skill gaps.
2. Suggest relevant online courses from Udemy, Coursera, edX, Infosys Springboard.
3. Provide the order in which the skills should be learned.
4. Give an estimated timeline for each skill/course (e.g., 1-2 weeks, 2-3 weeks or in months).

Important: Return ONLY a JSON array of objects with keys:
- skill
- recommended_course
- platform
- estimated_duration
Do NOT include explanations, Markdown, or extra text.
"""

    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
    chain = LLMChain(llm=llm, prompt=PromptTemplate(template=prompt, input_variables=[]))

    # Call GPT
    response = chain.invoke({})  # returns dict like {"text": "..."} in some versions

    # If GPT returns a dict with 'text', extract it
    if isinstance(response, dict) and "text" in response:
        response_text = response["text"]
    else:
        response_text = str(response)

    # Clean up code fences
    response_text = response_text.replace("```json", "").replace("```", "").strip()

    # Parse JSON
    try:
        roadmap = json.loads(response_text)
    except json.JSONDecodeError:
        roadmap = [{"message": "Failed to parse GPT JSON output. Raw output: " + response_text}]

    # Ensure always a list
    if not isinstance(roadmap, list):
        roadmap = [roadmap]

    return roadmap
