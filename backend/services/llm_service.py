from groq import Groq
from config import GROQ_API_KEY
import json

client = Groq(api_key=GROQ_API_KEY)

def generate_worksheet_content(
    topic: str = None,
    code: str = None,
    description: str = None,
    custom_instructions: str = None,
    sections: list = None,
    programming_language: str = "Python",
    web_content: str = None
) -> dict:

    topic_line = f"Topic: {topic}" if topic else "Topic: Not provided — analyze the code below"
    code_line = f"Student's Code:\n{code}" if code else "Code: Not provided — generate appropriate code"
    description_line = f"Extra Description: {description}" if description else ""
    instructions_line = f"Custom Instructions: {custom_instructions}" if custom_instructions else ""
    web_line = f"Reference Content from Web:\n{web_content}" if web_content else ""
    sections_line = ", ".join(sections) if sections else "objective, theory, code, learning_outcomes"

    prompt = f"""
You are an expert college lab worksheet generator.

{topic_line}
{description_line}
{code_line}
{instructions_line}
Programming Language: {programming_language}

{web_line}

Generate a complete college lab worksheet with these sections ONLY: {sections_line}

STRICT RULES:
- Return ONLY a valid JSON object, nothing else
- No extra text, no markdown, no backticks
- Keep theory clear and simple for undergraduate students
- Code must be properly commented
- Learning outcomes must be specific and measurable

Return this exact JSON structure:
{{
    "title": "worksheet title here",
    "objective": "objective text here",
    "theory": "theory text here",
    "algorithm": ["step 1", "step 2", "step 3"],
    "code": "code here",
    "expected_output": "expected output here",
    "learning_outcomes": ["outcome 1", "outcome 2", "outcome 3"],
    "viva_questions": ["question 1", "question 2"],
    "references": ["reference 1", "reference 2"],
    "conclusion": "conclusion text here"
}}

Only include sections that were requested: {sections_line}
For unrequested sections, set their value to null.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert worksheet generator. Always return valid JSON only. Never add any text outside the JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=3000
    )

    raw = response.choices[0].message.content.strip()

    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        return result
    except json.JSONDecodeError:
        return {
            "title": topic or "Worksheet",
            "error": "Failed to parse LLM response",
            "raw": raw
        }