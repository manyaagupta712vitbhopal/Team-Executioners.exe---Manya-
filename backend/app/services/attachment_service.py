"""
Planner attachment service.

Lets a user attach a file (PDF, image, plain text, etc.) to a Task or
Assignment. When the file's text can be extracted (PDFs and plain-text
files today), the extracted text is cached on disk so the mentor
service can feed it to Gemini and ground its recommendations in the
file's real content instead of just the item's title.
"""

import os
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.attachment import PlannerAttachment
from app.models.assignment import Assignment
from app.models.planner import Planner
from app.models.task import Task
from app.services.pdf_service import extract_pdf_text

ATTACHMENTS_SUBDIR = "planner_attachments"
MAX_EXTRACTED_CHARS = 20000

PLAIN_TEXT_MIME_TYPES = {"text/plain", "text/markdown", "text/csv"}

_ATTACHMENTS_DIR = os.path.join(settings.UPLOAD_DIR, ATTACHMENTS_SUBDIR)
os.makedirs(_ATTACHMENTS_DIR, exist_ok=True)
os.makedirs(settings.EXTRACTED_TEXT_DIR, exist_ok=True)


def _get_owned_task(db: Session, task_id: int, user_id: int) -> Task:
    task = (
        db.query(Task)
        .join(Planner, Task.planner_id == Planner.id)
        .filter(Task.id == task_id, Planner.user_id == user_id)
        .first()
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found."
        )
    return task


def _get_owned_assignment(db: Session, assignment_id: int, user_id: int) -> Assignment:
    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id, Assignment.user_id == user_id)
        .first()
    )
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found."
        )
    return assignment


def _try_extract(file_path: str, mime_type: str | None) -> str | None:
    """
    Best-effort text extraction. Returns None (not raises) for
    unsupported types or unreadable files, since an attachment that
    can't be parsed should still upload successfully.
    """
    try:
        if mime_type == "application/pdf":
            return extract_pdf_text(file_path)
        if mime_type in PLAIN_TEXT_MIME_TYPES:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception:
        return None
    return None


def _save_upload(file: UploadFile, user_id: int) -> tuple[str, int]:
    unique_filename = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(_ATTACHMENTS_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        content = file.file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is too large.",
            )
        buffer.write(content)

    return file_path, os.path.getsize(file_path)


def _create_attachment(
    *,
    db: Session,
    file: UploadFile,
    user_id: int,
    task_id: int | None = None,
    assignment_id: int | None = None,
) -> PlannerAttachment:
    file_path, file_size = _save_upload(file, user_id)

    extracted_text = _try_extract(file_path, file.content_type)

    text_path = None
    extracted = False
    if extracted_text and extracted_text.strip():
        text_filename = f"attachment_{uuid4().hex}.txt"
        text_path = os.path.join(settings.EXTRACTED_TEXT_DIR, text_filename)
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(extracted_text[:MAX_EXTRACTED_CHARS])
        extracted = True

    attachment = PlannerAttachment(
        filename=file.filename,
        file_path=file_path,
        mime_type=file.content_type,
        file_size=file_size,
        extracted=extracted,
        text_path=text_path,
        task_id=task_id,
        assignment_id=assignment_id,
        user_id=user_id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def add_task_attachment(
    *, db: Session, task_id: int, file: UploadFile, user_id: int
) -> PlannerAttachment:
    _get_owned_task(db, task_id, user_id)
    return _create_attachment(db=db, file=file, user_id=user_id, task_id=task_id)


def add_assignment_attachment(
    *, db: Session, assignment_id: int, file: UploadFile, user_id: int
) -> PlannerAttachment:
    _get_owned_assignment(db, assignment_id, user_id)
    return _create_attachment(
        db=db, file=file, user_id=user_id, assignment_id=assignment_id
    )


def delete_attachment(*, db: Session, attachment_id: int, user_id: int) -> dict:
    attachment = (
        db.query(PlannerAttachment)
        .filter(
            PlannerAttachment.id == attachment_id,
            PlannerAttachment.user_id == user_id,
        )
        .first()
    )
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found."
        )

    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)
    if attachment.text_path and os.path.exists(attachment.text_path):
        os.remove(attachment.text_path)

    db.delete(attachment)
    db.commit()
    return {"message": "Attachment deleted successfully."}


def load_attachment_text(attachment: PlannerAttachment) -> str | None:
    """Read cached extracted text for an attachment, if any."""
    if not attachment.text_path or not os.path.exists(attachment.text_path):
        return None
    with open(attachment.text_path, "r", encoding="utf-8") as f:
        return f.read()
