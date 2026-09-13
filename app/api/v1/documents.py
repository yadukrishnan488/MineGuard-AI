import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.permissions import get_current_user, RoleChecker, verify_mine_access
from app.models.enums import UserRole, DocumentOCRStatus
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, OCRReviewRequest
from app.integrations.ocr.ocr_service import OCRService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/documents", tags=["Document Processing & OCR"])


@router.post(
    "/ocr",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.MINE_MANAGER, UserRole.FIELD_INSPECTOR, UserRole.CORPORATE_ADMIN]))],
)
def upload_and_process_document(
    file: UploadFile = File(...),
    mine_id: str = Form(...),
    category: str = Form("COMPLIANCE_CERTIFICATE"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload compliance documents or mining licenses and run Tesseract OCR text extraction.
    OCR results are marked UNVERIFIED until validated by an authorized officer.
    """
    verify_mine_access(current_user, mine_id)

    orig_name, file_path, file_size, extracted_text, confidence, ocr_status = OCRService.save_and_extract(
        file=file,
        mine_id=mine_id,
        uploaded_by_id=current_user.id,
        category=category,
    )

    doc = Document(
        file_name=orig_name,
        file_path=file_path,
        file_type=orig_name.split(".")[-1].upper(),
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/octet-stream",
        document_category=category,
        mine_id=mine_id,
        uploaded_by_id=current_user.id,
        ocr_status=ocr_status,
        ocr_extracted_text=extracted_text,
        ocr_confidence=confidence,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    AuditService.create_audit_entry(
        db,
        actor_id=current_user.id,
        action="UPLOAD_DOCUMENT_OCR",
        entity_type="DOCUMENT",
        entity_id=doc.id,
        change_metadata={"filename": orig_name, "category": category, "ocr_confidence": confidence},
    )
    return doc


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve document metadata, extracted OCR text, and verification status."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    verify_mine_access(current_user, doc.mine_id)
    return doc


@router.get("/{document_id}/status")
def get_document_ocr_status(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check asynchronous OCR status and confidence."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    verify_mine_access(current_user, doc.mine_id)
    return {
        "document_id": doc.id,
        "ocr_status": doc.ocr_status.value,
        "ocr_confidence": doc.ocr_confidence,
        "is_verified": doc.ocr_status == DocumentOCRStatus.VERIFIED,
    }


@router.patch(
    "/{document_id}/review",
    response_model=DocumentResponse,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.MINE_MANAGER, UserRole.CORPORATE_ADMIN, UserRole.AUDITOR]))],
)
def review_and_verify_ocr(
    document_id: str,
    review_in: OCRReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Human-in-the-loop review: Approve, correct, or certify extracted statutory document text.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    verify_mine_access(current_user, doc.mine_id)

    doc.ocr_extracted_text = review_in.verified_text
    doc.ocr_status = DocumentOCRStatus.VERIFIED if review_in.approve else DocumentOCRStatus.UNVERIFIED
    doc.verified_by_id = current_user.id
    doc.verified_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(doc)

    AuditService.create_audit_entry(
        db,
        actor_id=current_user.id,
        action="VERIFY_DOCUMENT_OCR",
        entity_type="DOCUMENT",
        entity_id=doc.id,
        change_metadata={"status": doc.ocr_status.value},
    )
    return doc


@router.get("/{document_id}/download")
def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Secure authorized streaming of private documents. Never exposed through public URLs.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    verify_mine_access(current_user, doc.mine_id)

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file missing on disk")

    return FileResponse(
        path=doc.file_path,
        media_type=doc.mime_type,
        filename=doc.file_name,
    )
