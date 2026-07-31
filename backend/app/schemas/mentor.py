from pydantic import BaseModel


class MentorPriorityItem(BaseModel):
    title: str
    why: str
    urgency: str  # "high" | "medium" | "low"


class MentorScheduleBlock(BaseModel):
    time: str
    activity: str


class MentorFileInsight(BaseModel):
    source: str  # attachment filename
    insight: str


class MentorAttachmentSnapshot(BaseModel):
    filename: str
    excerpt: str | None = None


class MentorTaskSnapshot(BaseModel):
    title: str
    completed: bool
    attachments: list[MentorAttachmentSnapshot] = []


class MentorAssignmentSnapshot(BaseModel):
    title: str
    due_date: str | None = None
    priority: str | None = None
    attachments: list[MentorAttachmentSnapshot] = []


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
    file_insights: list[MentorFileInsight] = []
    context: MentorContext
