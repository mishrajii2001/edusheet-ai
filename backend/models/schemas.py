from pydantic import BaseModel
from typing import List, Optional

class FormattingSettings(BaseModel):
    font_family: str = "Times New Roman"
    heading_size: int = 14
    subheading_size: int = 13
    body_size: int = 12
    alignment: str = "justified"
    margin: float = 1.0
    line_spacing: float = 1.5

class WorksheetRequest(BaseModel):
    topic: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    custom_instructions: Optional[str] = None
    sections: List[str]
    programming_language: str = "Python"
    formatting: FormattingSettings

class WorksheetResponse(BaseModel):
    success: bool
    message: str
    file_name: Optional[str] = None