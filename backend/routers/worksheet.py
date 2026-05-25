from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import FileResponse
from models.schemas import WorksheetResponse
from services.search_service import search_web
from services.llm_service import generate_worksheet_content
from services.vectordb_service import store_web_content, retrieve_web_content
from services.document_service import create_worksheet
import json
import os
import shutil
import uuid
from PIL import Image as PILImage

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_IMAGE_WIDTH = 1200

def compress_image(filepath: str) -> str:
    try:
        img = PILImage.open(filepath)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.width > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_IMAGE_WIDTH, new_height), PILImage.LANCZOS)
        compressed_path = filepath.rsplit(".", 1)[0] + "_compressed.jpg"
        img.save(compressed_path, "JPEG", quality=85, optimize=True)
        os.remove(filepath)
        return compressed_path
    except Exception as e:
        print(f"Image compression failed: {str(e)}")
        return filepath

@router.post("/generate")
async def generate_worksheet(
    topic: str = Form(None),
    description: str = Form(None),
    code: str = Form(None),
    custom_instructions: str = Form(None),
    sections: str = Form(...),
    programming_language: str = Form("Python"),
    formatting: str = Form(...),
    image_data: str = Form(None),
    image1: UploadFile = File(None),
    image2: UploadFile = File(None),
    image3: UploadFile = File(None),
    header_image: UploadFile = File(None),
):
    try:
        try:
            sections_list = json.loads(sections)
        except:
            sections_list = [s.strip() for s in sections.split(",")]

        formatting_dict = json.loads(formatting)
        image_metadata = json.loads(image_data) if image_data else []

        if not topic and not code:
            raise HTTPException(
                status_code=400,
                detail="Please provide either a topic or paste your code"
            )

        saved_images = {}
        uploaded_files = [image1, image2, image3]

        for i, image in enumerate(uploaded_files):
            if not image or not image.filename:
                continue
            try:
                ext = image.filename.split(".")[-1].lower()
                if ext not in ["jpg", "jpeg", "png", "gif", "bmp", "webp"]:
                    continue
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, "wb") as f:
                    shutil.copyfileobj(image.file, f)
                filepath = compress_image(filepath)
                meta = image_metadata[i] if i < len(image_metadata) else {}
                section_key = meta.get("section", "expected_output")
                caption = meta.get("caption", f"Figure {i+1}: {image.filename}")
                if section_key not in saved_images:
                    saved_images[section_key] = []
                saved_images[section_key].append({
                    "path": filepath,
                    "caption": caption
                })
                print(f"Image {i+1} saved: {filepath} → section: {section_key}")
            except Exception as e:
                print(f"Image {i+1} processing failed: {str(e)}")
                continue

        header_image_path = None
        if header_image and header_image.filename:
            try:
                ext = header_image.filename.split(".")[-1].lower()
                filename = f"header_{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, "wb") as f:
                    shutil.copyfileobj(header_image.file, f)
                header_image_path = compress_image(filepath)
                print(f"Header image saved: {header_image_path}")
            except Exception as e:
                print(f"Header image processing failed: {str(e)}")

        web_content = None
        if topic:
            print("Checking ChromaDB for web content...")
            web_content = retrieve_web_content(topic)
            if web_content:
                print("Found cached web content!")
            else:
                print("Searching web...")
                web_content = search_web(topic)
                if web_content:
                    store_web_content(topic, web_content)
                    print("Web content cached!")

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

        print("Creating worksheet document...")
        file_name = create_worksheet(
            content=content,
            formatting=formatting_dict,
            images=saved_images if saved_images else None,
            header_image=header_image_path
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