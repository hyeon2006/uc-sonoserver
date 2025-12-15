from pydantic import BaseModel
from helpers.sonolus_typings import Icon, ServerInfoButtonType, Text

class Tag(BaseModel):
    title: Text | str
    icon: Icon | str | None = None


class SRL(BaseModel):
    hash: str | None = None
    url: str | None = None


class SIL(BaseModel):
    address: str
    name: str

class ServerInfoButton(BaseModel):
    type: ServerInfoButtonType

class ServerItemLeaderboard(BaseModel):
    name: str
    title: str | Text
    description: str | None = None

class ServerMessage(BaseModel):
    message: str

class ServerItemLeaderboardRecord(BaseModel):
    name: str
    rank: Text | str
    player: str
    value: Text | str
