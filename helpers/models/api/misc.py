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

class ReplayUploadData(BaseModel):
    engine: str
    nperfect: int
    ngreat: int
    ngood: int
    nmiss: int
    arcade_score: int
    accuracy_score: int
    speed: float

class Leaderboard(ReplayUploadData):
    submitter: str
    replay_data_hash: str
    replay_config_hash: str
    chart_id: str

class LeaderboardDBResponse(Leaderboard):
    display_name: str
    id: int
    created_at: datetime
    chart_prefix: str

class LeaderboardInfo(BaseModel):
    pageCount: int
    data: list[LeaderboardDBResponse]