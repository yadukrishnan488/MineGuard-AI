from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.enums import DocumentOCRStatus


class DocumentResponse(BaseModel):
    id: str
    file_name: str
    file_type: str
    file_size_bytes: int
    mime_type: str
    document_category: str
    mine_id: str
    uploaded_by_id: str
    ocr_status: DocumentOCRStatus
    ocr_extracted_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    verified_by_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OCRReviewRequest(BaseModel):
    verified_text: str
    approve: bool = True
