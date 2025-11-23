from pydantic import BaseModel
from datetime import datetime

class Account(BaseModel):
    sonolus_id: str
    sonolus_handle: int
    sonolus_username: str
    created_at: datetime
    mod: bool | None = None
    admin: bool | None = None # TODO (backend): make these non-optional
    unread_notifications: int

class AuthenticationData(BaseModel):
    session: str
    expiry: int