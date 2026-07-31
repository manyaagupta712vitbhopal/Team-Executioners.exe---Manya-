from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    id: int
    filename: str
    mime_type: str | None = None
    file_size: int | None = None
    extracted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
