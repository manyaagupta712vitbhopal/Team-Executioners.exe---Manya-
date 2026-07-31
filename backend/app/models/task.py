from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)

    title = Column(String)

    completed = Column(Boolean, default=False)

    planner_id = Column(Integer, ForeignKey("planners.id"))

    planner = relationship("Planner", back_populates="tasks")

    attachments = relationship(
        "PlannerAttachment",
        back_populates="task",
        cascade="all, delete-orphan",
    )