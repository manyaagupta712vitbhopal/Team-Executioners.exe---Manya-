from datetime import date

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------- #
# Tasks (today's planner)
# --------------------------------------------------------------------------- #

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------- #
# Assignments
# --------------------------------------------------------------------------- #

class AssignmentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    due_date: date | None = None
    priority: str | None = Field(
        default=None, description='One of "high", "medium", "low".'
    )


class AssignmentResponse(BaseModel):
    id: int
    title: str
    due_date: date | None = None
    priority: str | None = None
    completed: bool

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------- #
# Deadlines
# --------------------------------------------------------------------------- #

class DeadlineCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    deadline: date | None = None
    type: str | None = Field(default=None, max_length=50)


class DeadlineResponse(BaseModel):
    id: int
    title: str
    deadline: date | None = None
    type: str | None = None

    model_config = ConfigDict(from_attributes=True)
