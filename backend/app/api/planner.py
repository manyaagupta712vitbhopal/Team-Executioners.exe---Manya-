from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.planner import (
    AssignmentCreate,
    AssignmentResponse,
    DeadlineCreate,
    DeadlineResponse,
    TaskCreate,
    TaskResponse,
)
from app.services.planner_service import (
    add_assignment,
    add_deadline,
    add_task,
    complete_assignment,
    delete_assignment,
    delete_deadline,
    delete_task,
    list_assignments,
    list_deadlines,
    list_today_tasks,
    toggle_task,
)

router = APIRouter(prefix="/planner", tags=["Planner"])


# --------------------------------------------------------------------------- #
# Tasks
# --------------------------------------------------------------------------- #

@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a task to today's planner",
)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    return add_task(db=db, title=payload.title, user_id=current_user.id)


@router.get(
    "/tasks/today",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List today's tasks",
)
def read_today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskResponse]:
    return list_today_tasks(db=db, user_id=current_user.id)


@router.patch(
    "/tasks/{task_id}/toggle",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle a task's completed status",
)
def update_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    return toggle_task(db=db, task_id=task_id, user_id=current_user.id)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a task",
)
def remove_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return delete_task(db=db, task_id=task_id, user_id=current_user.id)


# --------------------------------------------------------------------------- #
# Assignments
# --------------------------------------------------------------------------- #

@router.post(
    "/assignments",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an assignment",
)
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssignmentResponse:
    return add_assignment(
        db=db,
        title=payload.title,
        due_date=payload.due_date,
        priority=payload.priority,
        user_id=current_user.id,
    )


@router.get(
    "/assignments",
    response_model=list[AssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List open assignments",
)
def read_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AssignmentResponse]:
    return list_assignments(db=db, user_id=current_user.id)


@router.patch(
    "/assignments/{assignment_id}/complete",
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark an assignment as completed",
)
def update_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssignmentResponse:
    return complete_assignment(
        db=db, assignment_id=assignment_id, user_id=current_user.id
    )


@router.delete(
    "/assignments/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an assignment",
)
def remove_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return delete_assignment(
        db=db, assignment_id=assignment_id, user_id=current_user.id
    )


# --------------------------------------------------------------------------- #
# Deadlines
# --------------------------------------------------------------------------- #

@router.post(
    "/deadlines",
    response_model=DeadlineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a deadline",
)
def create_deadline(
    payload: DeadlineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeadlineResponse:
    return add_deadline(
        db=db,
        title=payload.title,
        deadline=payload.deadline,
        type=payload.type,
        user_id=current_user.id,
    )


@router.get(
    "/deadlines",
    response_model=list[DeadlineResponse],
    status_code=status.HTTP_200_OK,
    summary="List deadlines",
)
def read_deadlines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DeadlineResponse]:
    return list_deadlines(db=db, user_id=current_user.id)


@router.delete(
    "/deadlines/{deadline_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a deadline",
)
def remove_deadline(
    deadline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return delete_deadline(db=db, deadline_id=deadline_id, user_id=current_user.id)
