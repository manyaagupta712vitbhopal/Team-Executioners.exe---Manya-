from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.assignment import Assignment
from app.models.deadline import Deadline
from app.models.planner import Planner
from app.models.task import Task


# --------------------------------------------------------------------------- #
# Tasks (today's planner)
# --------------------------------------------------------------------------- #

def _get_or_create_today_planner(db: Session, user_id: int) -> Planner:
    today = date.today()
    planner = (
        db.query(Planner)
        .filter(Planner.user_id == user_id, Planner.study_date == today)
        .first()
    )
    if planner is None:
        planner = Planner(user_id=user_id, study_date=today)
        db.add(planner)
        db.commit()
        db.refresh(planner)
    return planner


def add_task(*, db: Session, title: str, user_id: int) -> Task:
    planner = _get_or_create_today_planner(db, user_id)
    task = Task(title=title, planner_id=planner.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_today_tasks(*, db: Session, user_id: int) -> list[Task]:
    today = date.today()
    planner = (
        db.query(Planner)
        .options(joinedload(Planner.tasks).joinedload(Task.attachments))
        .filter(Planner.user_id == user_id, Planner.study_date == today)
        .first()
    )
    return planner.tasks if planner else []


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


def toggle_task(*, db: Session, task_id: int, user_id: int) -> Task:
    task = _get_owned_task(db, task_id, user_id)
    task.completed = not task.completed
    db.commit()
    db.refresh(task)
    return task


def delete_task(*, db: Session, task_id: int, user_id: int) -> dict:
    task = _get_owned_task(db, task_id, user_id)
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully."}


# --------------------------------------------------------------------------- #
# Assignments
# --------------------------------------------------------------------------- #

def add_assignment(
    *,
    db: Session,
    title: str,
    due_date: date | None,
    priority: str | None,
    user_id: int,
) -> Assignment:
    assignment = Assignment(
        title=title, due_date=due_date, priority=priority, user_id=user_id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def list_assignments(*, db: Session, user_id: int) -> list[Assignment]:
    return (
        db.query(Assignment)
        .options(joinedload(Assignment.attachments))
        .filter(Assignment.user_id == user_id, Assignment.completed.is_(False))
        .order_by(Assignment.due_date.asc().nullslast())
        .all()
    )


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


def complete_assignment(*, db: Session, assignment_id: int, user_id: int) -> Assignment:
    assignment = _get_owned_assignment(db, assignment_id, user_id)
    assignment.completed = True
    db.commit()
    db.refresh(assignment)
    return assignment


def delete_assignment(*, db: Session, assignment_id: int, user_id: int) -> dict:
    assignment = _get_owned_assignment(db, assignment_id, user_id)
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted successfully."}


# --------------------------------------------------------------------------- #
# Deadlines
# --------------------------------------------------------------------------- #

def add_deadline(
    *,
    db: Session,
    title: str,
    deadline: date | None,
    type: str | None,
    user_id: int,
) -> Deadline:
    obj = Deadline(title=title, deadline=deadline, type=type, user_id=user_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_deadlines(*, db: Session, user_id: int) -> list[Deadline]:
    return (
        db.query(Deadline)
        .filter(Deadline.user_id == user_id)
        .order_by(Deadline.deadline.asc().nullslast())
        .all()
    )


def delete_deadline(*, db: Session, deadline_id: int, user_id: int) -> dict:
    obj = (
        db.query(Deadline)
        .filter(Deadline.id == deadline_id, Deadline.user_id == user_id)
        .first()
    )
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found."
        )
    db.delete(obj)
    db.commit()
    return {"message": "Deadline deleted successfully."}
