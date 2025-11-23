from datetime import datetime
from pydantic import BaseModel

class Comment(BaseModel):
    id: int
    commenter: str
    username: str | None = None
    content: str
    created_at: int
    deleted_at: int | None = None
    chart_id: str
    owner: bool | None = None

class DeleteCommentResponse(BaseModel):
    id: int
    commenter: str
    username: str | None = None
    content: str
    created_at: datetime # TODO (backend): can't inherit from Comment because there's datetime here
    deleted_at: datetime | None = None
    chart_id: str
    owner: bool | None = None
    mod: bool | None = None

class CommentList(BaseModel):
    data: list[Comment]
    pageCount: int
    mod: bool | None = None
    admin: bool | None = None
