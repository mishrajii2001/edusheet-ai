from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import GROQ_API_KEY
import json

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=3000
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are an expert college lab worksheet generator.
Always return ONLY a valid JSON object.
Never add any text outside the JSON.
Never add markdown or backticks."""),
    ("human", """
Generate a college lab worksheet for the following:

Topic: {topic}
Description: {description}
Student Code: {code}
Custom Instructions: {custom_instructions}
Programming Language: {programming_language}
Sections Needed: {sections}

Reference Content:
{web_content}

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

Only include sections requested: {sections}
Set unrequested sections to null.
""")
])

parser = StrOutputParser()

chain = prompt_template | llm | parser

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
        clean = response.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        return result
    except json.JSONDecodeError:
        return {
            "title": topic or "Worksheet",
            "error": "Failed to parse LLM response",
            "raw": response
        }