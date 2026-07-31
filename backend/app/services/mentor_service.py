"""
Mentor agent service.

Gathers a snapshot of the current user's real workload — today's planned
tasks, upcoming assignments/deadlines, and today's study activity — and
hands it to the AI service to produce a mentor-style daily briefing
(priorities, a time-blocked schedule, and motivation).

No new database tables are used; this reads from models that already
exist (Planner, Task, Assignment, Deadline, StudySession, Pomodoro).
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload

from app.models.assignment import Assignment
from app.models.deadline import Deadline
from app.models.planner import Planner
from app.models.pomodoro import Pomodoro
from app.models.study_session import StudySession
from app.models.task import Task
from app.models.user import User
from app.services import ai_service
from app.services.attachment_service import load_attachment_text

LOOKAHEAD_DAYS = 7
MAX_ATTACHMENT_CHARS_PER_FILE = 4000  # keep the mentor prompt small & cheap


def _summarize_attachments(attachments: list) -> list[dict]:
    """
    Turn a Task's/Assignment's attachments into small JSON-safe dicts for
    the mentor prompt: filename plus a clipped excerpt of extracted text
    (when available) so Gemini can ground recommendations in the file's
    real content, not just its name.
    """
    summaries = []
    for att in attachments:
        excerpt = None
        if att.extracted:
            text = load_attachment_text(att)
            if text:
                excerpt = text.strip()[:MAX_ATTACHMENT_CHARS_PER_FILE]
        summaries.append({
            "filename": att.filename,
            "excerpt": excerpt,  # None if not extractable (e.g. an image)
        })
    return summaries


def _build_context(db: Session, user: User) -> dict:
    today = date.today()
    week_ahead = today + timedelta(days=LOOKAHEAD_DAYS)

    planner = (
        db.query(Planner)
        .options(joinedload(Planner.tasks).joinedload(Task.attachments))
        .filter(Planner.user_id == user.id, Planner.study_date == today)
        .first()
    )
    today_tasks = planner.tasks if planner else []

    assignments = (
        db.query(Assignment)
        .options(joinedload(Assignment.attachments))
        .filter(
            Assignment.user_id == user.id,
            Assignment.completed.is_(False),
            Assignment.due_date.isnot(None),
            Assignment.due_date <= week_ahead,
        )
        .order_by(Assignment.due_date.asc())
        .all()
    )

    deadlines = (
        db.query(Deadline)
        .filter(
            Deadline.user_id == user.id,
            Deadline.deadline.isnot(None),
            Deadline.deadline <= week_ahead,
        )
        .order_by(Deadline.deadline.asc())
        .all()
    )

    todays_sessions = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == user.id,
            StudySession.start_time >= today,
        )
        .all()
    )
    minutes_studied_today = sum(s.total_minutes or 0 for s in todays_sessions)

    todays_pomodoros = (
        db.query(Pomodoro)
        .filter(
            Pomodoro.user_id == user.id,
            Pomodoro.session_time >= today,
        )
        .count()
    )

    return {
        "today": today.isoformat(),
        "tasks": [
            {
                "title": t.title,
                "completed": bool(t.completed),
                "attachments": _summarize_attachments(t.attachments),
            }
            for t in today_tasks
        ],
        "assignments": [
            {
                "title": a.title,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "priority": a.priority,
                "attachments": _summarize_attachments(a.attachments),
            }
            for a in assignments
        ],
        "deadlines": [
            {
                "title": d.title,
                "date": d.deadline.isoformat() if d.deadline else None,
                "type": d.type,
            }
            for d in deadlines
        ],
        "minutes_studied_today": minutes_studied_today,
        "pomodoros_completed_today": todays_pomodoros,
    }


def get_daily_briefing(db: Session, user: User) -> dict:
    """
    Builds today's mentor briefing for the given user. Computed live on
    every call (no caching/persistence), so it always reflects the
    latest tasks/assignments/deadlines.
    """
    context = _build_context(db, user)
    briefing = ai_service.generate_daily_mentor_briefing(
        user_name=user.name,
        context=context,
    )
    briefing["context"] = context
    return briefing
