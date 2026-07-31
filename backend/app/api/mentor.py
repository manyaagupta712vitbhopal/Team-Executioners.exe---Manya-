from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.mentor import MentorBriefingResponse
from app.services.mentor_service import get_daily_briefing

router = APIRouter(prefix="/mentor", tags=["Mentor"])


@router.get(
    "/daily",
    response_model=MentorBriefingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get today's AI mentor briefing (priorities, schedule, motivation)",
)
def read_daily_briefing(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MentorBriefingResponse:
    return get_daily_briefing(db=db, user=current_user)
