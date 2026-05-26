from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import GROQ_API_KEY
import json
import re

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=3000
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are an expert college lab worksheet generator for Indian universities.
You generate detailed, accurate, and well-structured lab worksheets.
CRITICAL: Always return ONLY a valid JSON object.
CRITICAL: Never add backticks or markdown formatting.
CRITICAL: Never add any text before or after the JSON.
CRITICAL: In the code field, use \\n for line breaks. Never use triple quotes or actual newlines inside JSON strings.
CRITICAL: All string values in JSON must be on a single line with \\n for newlines.
Start your response directly with the opening curly brace of JSON.
Generate content detailed enough for a 3-4 page worksheet."""),

    ("human", """
Generate a detailed college lab worksheet for the following:

Topic: {topic}
Description: {description}
Student Code: {code}
Programming Language: {programming_language}

Reference Content from Web:
{web_content}

IMPORTANT Instructions (follow strictly):
{custom_instructions}

Generate worksheet with EXACTLY these sections: {sections}

STRICT CONTENT RULES:
- Theory must be AT LEAST 150-200 words with proper explanation
- Algorithm must have AT LEAST 8-10 detailed steps
- Code must be complete, working, and well commented
- Code field must use \\n for line breaks, never actual newlines
- Learning outcomes must have AT LEAST 5 specific points
- Viva questions must have AT LEAST 5 questions with answers
- Conclusion must be AT LEAST 80-100 words
- Objective must clearly state the purpose in 3-4 lines
- References must include at least 3 real sources
- Every section must have substantial, meaningful content
- Content should be appropriate for MCA/B.Tech/BCA level students

Return JSON with exactly these keys:
{{
    "title": "proper worksheet title",
    "aim": "clear aim in 2-3 lines if requested",
    "introduction": "detailed introduction if requested",
    "objective": "detailed objective in 3-4 lines",
    "apparatus": "tools and software needed if requested",
    "theory": "detailed theory minimum 150 words",
    "algorithm": ["detailed step 1", "detailed step 2", "at least 8 steps"],
    "code": "line1\\nline2\\nline3 - use \\n not actual newlines",
    "expected_output": "detailed expected output description",
    "result": "result section if requested",
    "learning_outcomes": ["outcome 1", "outcome 2", "outcome 3", "outcome 4", "outcome 5"],
    "viva_questions": ["Q1: question? Ans: answer", "Q2: question? Ans: answer", "at least 5"],
    "references": ["Author, Title, Year", "reference 2", "reference 3"],
    "conclusion": "detailed conclusion minimum 80 words"
}}

Only include sections from this list: {sections}
Set ALL other sections to null.
Any custom section names add them as new keys with detailed generated content.
""")
])

parser = StrOutputParser()
chain = prompt_template | llm | parser

def clean_json_string(text: str) -> str:
    text = text.strip()
    text = text.replace("```json", "").replace("```JSON", "").replace("```", "")
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    text = re.sub(r'"""\s*', '"', text)
    text = re.sub(r'\s*"""', '"', text)
    text = re.sub(r'(?<!\\)\n(?=[^"]*"[^"]*(?:"[^"]*"[^"]*)*$)', '\\n', text)
    return text

def generate_worksheet_content(
    topic=None,
    code=None,
    description=None,
    custom_instructions=None,
    sections=None,
    programming_language="Python",
    web_content=None
) -> dict:

    response = chain.invoke({
        "topic": topic or "Not provided - analyze the code",
        "code": code or "Not provided - generate appropriate code",
        "description": description or "",
        "custom_instructions": custom_instructions or "",
        "programming_language": programming_language,
        "sections": ", ".join(sections) if sections else "objective, theory, code, learning_outcomes",
        "web_content": web_content or "Not available - use your knowledge"
    })

    try:
        clean = clean_json_string(response)
        result = json.loads(clean)
        return result

    except json.JSONDecodeError:
        try:
            clean = clean_json_string(response)
            clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', clean)
            clean = re.sub(r',\s*}', '}', clean)
            clean = re.sub(r',\s*]', ']', clean)
            result = json.loads(clean)
            return result
        except json.JSONDecodeError:
            try:
                import ast
                clean = clean_json_string(response)
                result = ast.literal_eval(clean)
                return result
            except:
                return {
                    "title": topic or "Worksheet",
                    "objective": "Content generated but formatting failed. Please try again.",
                    "theory": response[:500] if response else "Generation failed",
                    "error_note": "Partial content - regenerate for better results"
                }