from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import FileResponse
from models.schemas import WorksheetResponse
from services.search_service import search_web
from services.llm_service import generate_worksheet_content
from services.vectordb_service import store_worksheet, retrieve_worksheet
from services.document_service import create_worksheet
import json
import os

router = APIRouter()

@router.post("/generate")
async def generate_worksheet(
    topic: str = Form(None),
    description: str = Form(None),
    code: str = Form(None),
    custom_instructions: str = Form(None),
    sections: str = Form(...),
    programming_language: str = Form("Python"),
    formatting: str = Form(...)
):
    try:
        try:
            sections_list = json.loads(sections)
        except:
            sections_list = [s.strip() for s in sections.split(",")]

        formatting_dict = json.loads(formatting)

        if not topic and not code:
            raise HTTPException(
                status_code=400,
                detail="Please provide either a topic or paste your code"
            )

        content = None
        if topic:
            print(f"Checking ChromaDB for: {topic}")
            content = retrieve_worksheet(topic)
            if content:
                print("Found in ChromaDB! Skipping web search.")

        if not content:
            web_content = None
            if topic:
                print("Searching web...")
                web_content = search_web(topic)

            print("Generating with LLM...")
            content = generate_worksheet_content(
                topic=topic,
                code=code,
                description=description,
                custom_instructions=custom_instructions,
                sections=sections_list,
                programming_language=programming_language,
                web_content=web_content
            )

            if topic and content:
                store_worksheet(topic, content)
                print("Stored in ChromaDB!")

        print("Creating worksheet document...")
        file_name = create_worksheet(
            content=content,
            formatting=formatting_dict,
            images=None
        )

        return WorksheetResponse(
            success=True,
            message="Worksheet generated successfully!",
            file_name=file_name
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{file_name}")
async def download_worksheet(file_name: str):
    file_path = os.path.join(
        os.path.dirname(__file__), "..", "generated", file_name
    )
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )