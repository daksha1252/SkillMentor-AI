import os
import json
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def suggest_projects(career_goal):
    """
    Suggest 3-5 practical projects based on the user's career goal.
    Returns a list of project dictionaries with:
    - project_name
    - description
    - estimated_duration
    """

    if not career_goal:
        return [{"message": "No career goal provided. Cannot suggest projects."}]

    prompt = f"""
You are a career mentor.

The user's career goal is: {career_goal}

Tasks:
1. Suggest 2-4 practical and real time projects the user can do to gain relevant knowledge and experience.
2. Provide a short description for each project.
3. Suggest an estimated timeline to complete each project.

Important:
- Return ONLY a JSON array of objects with keys:
  - project_name
  - description
  - estimated_duration
- Do NOT include explanations, Markdown, or text outside the JSON.
"""

    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
    chain = LLMChain(llm=llm, prompt=PromptTemplate(template=prompt, input_variables=[]))

    # Call GPT
    response = chain.invoke({})
    response_text = response.get("text", str(response)) if isinstance(response, dict) else str(response)

    # Clean code fences
    response_text = response_text.replace("```json", "").replace("```", "").strip()

    # Parse JSON
    try:
        projects = json.loads(response_text)
    except json.JSONDecodeError:
        projects = [{"message": "Failed to parse GPT JSON output. Raw output: " + response_text}]

    # Ensure output is always a list
    if not isinstance(projects, list):
        projects = [projects]

    return projects
