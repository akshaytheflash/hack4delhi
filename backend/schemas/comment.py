from pydantic import BaseModel, Field
from datetime import datetime

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: int
    report_id: int
    user_id: int
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
