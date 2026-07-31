from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class PlannerAttachment(Base):
    """
    A file attached to a planner Task or Assignment.

    Exactly one of task_id / assignment_id is set. When the file's text
    can be extracted (currently: PDFs and plain text files), it's saved
    to text_path so the mentor service can read it and ground its
    recommendations in the file's actual content rather than just the
    title.
    """

    __tablename__ = "planner_attachments"

    id = Column(Integer, primary_key=True)

    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)

    extracted = Column(Boolean, default=False, nullable=False)
    text_path = Column(String(500), nullable=True)

    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    assignment_id = Column(
        Integer,
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("Task", back_populates="attachments")
    assignment = relationship("Assignment", back_populates="attachments")
