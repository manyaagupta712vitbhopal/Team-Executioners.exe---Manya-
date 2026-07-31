from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)

    due_date = Column(Date)

    completed = Column(Boolean, default=False)

    priority = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="assignments")

    attachments = relationship(
        "PlannerAttachment",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )
