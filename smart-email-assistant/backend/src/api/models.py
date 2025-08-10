from pydantic import BaseModel
from typing import List, Optional

class EmailProcessRequest(BaseModel):
    days_to_process: int = 7
    enable_reply_generation: bool = True

class EmailSummaryResponse(BaseModel):
    id: str # Add id field
    sender: str
    subject: str
    date: str
    summary: str
    replied: bool
    draftReply: str
    priority: str
    threadId: str

class ExportRequest(BaseModel):
    filename: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str = "ok"
    message: str = "API is running"

class ErrorResponse(BaseModel):
    detail: str
