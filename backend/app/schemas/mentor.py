from pydantic import BaseModel


class MentorPriorityItem(BaseModel):
    title: str
    why: str
    urgency: str  # "high" | "medium" | "low"


class MentorScheduleBlock(BaseModel):
    time: str
    activity: str


class MentorTaskSnapshot(BaseModel):
    title: str
    completed: bool


class MentorAssignmentSnapshot(BaseModel):
    title: str
    due_date: str | None = None
    priority: str | None = None


class MentorDeadlineSnapshot(BaseModel):
    title: str
    date: str | None = None
    type: str | None = None


class MentorContext(BaseModel):
    today: str
    tasks: list[MentorTaskSnapshot] = []
    assignments: list[MentorAssignmentSnapshot] = []
    deadlines: list[MentorDeadlineSnapshot] = []
    minutes_studied_today: int = 0
    pomodoros_completed_today: int = 0


class MentorBriefingResponse(BaseModel):
    greeting: str
    motivation: str
    priorities: list[MentorPriorityItem]
    schedule: list[MentorScheduleBlock]
    tips: list[str]
    context: MentorContext
