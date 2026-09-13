from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import DocumentOCRStatus


class Document(Base, UUIDMixin, TimestampMixin):
    """Uploaded compliance evidence, mining licenses, and statutory certificates."""
    __tablename__ = "documents"

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PDF, PNG, JPG, JPEG
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_category: Mapped[str] = mapped_column(String(100), default="COMPLIANCE_CERTIFICATE", nullable=False)
    
    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # OCR Processing pipeline fields
    ocr_status: Mapped[DocumentOCRStatus] = mapped_column(
        SQLEnum(DocumentOCRStatus),
        default=DocumentOCRStatus.PENDING,
        nullable=False,
        index=True,
    )
    ocr_extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Verification workflow (human-in-the-loop review)
    verified_by_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    mine: Mapped["Mine"] = relationship("Mine", back_populates="documents")
    uploaded_by: Mapped["User"] = relationship("User", foreign_keys=[uploaded_by_id])
    verified_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[verified_by_id])
