from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from models.schemas import WorksheetRequest, WorksheetResponse
from services.search_service import search_web
from services.llm_service import generate_worksheet_content
from services.vectordb_service import store_worksheet, retrieve_worksheet
from services.document_service import create_worksheet
import json
import os
import shutil
import uuid

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/generate")
async def generate_worksheet(
    topic: str = Form(None),
    description: str = Form(None),
    code: str = Form(None),
    custom_instructions: str = Form(None),
    sections: str = Form(...),
    programming_language: str = Form("Python"),
    formatting: str = Form(...),
    images: list[UploadFile] = File(None),
    image_sections: str = Form(None)
):
    try:
        sections_list = json.loads(sections)
        formatting_dict = json.loads(formatting)

        if not topic and not code:
            raise HTTPException(
                status_code=400,
                detail="Please provide either a topic or paste your code"
            )

        saved_images = {}
        if images:
            image_sections_list = json.loads(image_sections) if image_sections else []
            for i, image in enumerate(images):
                section_key = image_sections_list[i] if i < len(image_sections_list) else "expected_output"
                ext = image.filename.split(".")[-1]
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, "wb") as f:
                    shutil.copyfileobj(image.file, f)
                if section_key not in saved_images:
                    saved_images[section_key] = []
                saved_images[section_key].append({
                    "path": filepath,
                    "caption": f"Figure: {image.filename}"
                })

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
            images=saved_images if saved_images else None
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