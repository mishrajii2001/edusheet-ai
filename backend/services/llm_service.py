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
Programming Language: {programming_language}

Reference Content:
{web_content}

IMPORTANT Custom Instructions (must follow strictly): {custom_instructions}

Generate worksheet with EXACTLY these sections: {sections}

STRICT RULES:
- Generate ALL sections listed above without exception
- For each section use the exact key name in JSON
- Return ONLY valid JSON, no extra text
- Use student code as-is in code section if provided
- For list sections like learning_outcomes, viva_questions return array of strings
- For code section return code as string
- All other sections return as string

Return JSON with exactly these keys plus title:
{{
    "title": "worksheet title here",
    "objective": "if requested",
    "theory": "if requested",
    "algorithm": ["step 1", "step 2"],
    "code": "if requested",
    "expected_output": "if requested",
    "learning_outcomes": ["outcome 1", "outcome 2"],
    "viva_questions": ["q1", "q2"],
    "references": ["ref1"],
    "conclusion": "if requested",
    "introduction": "if requested",
    "aim": "if requested",
    "task_to_be_done": "if requested",
    "apparatus": "if requested"
}}

Only include sections from this list: {sections}
Set ALL other sections to null.
Any custom section names not in the above template — add them as new keys with generated content.
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