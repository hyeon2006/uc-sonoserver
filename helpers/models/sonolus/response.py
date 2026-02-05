from typing import Annotated
from pydantic import BaseModel, Field

from helpers.models.sonolus.item import ReplayItem, ServerItem, ServerItemCommunityComment, ServerItemLeaderboard, ServerItemLeaderboardRecord
from helpers.models.sonolus.item_section import ServerItemSection
from helpers.models.sonolus.misc import SRL, ServerInfoItemButton
from helpers.models.sonolus.options import ServerForm, ServerOption


class ServerItemCommunityCommentList(BaseModel):
    pageCount: int
    cursor: str | None = None
    comments: list[ServerItemCommunityComment]

class ServerItemInfo(BaseModel):
    creates: list[ServerForm] | None = None
    searches: list[ServerForm] | None = None
    quickSearchValues: str | None = None
    sections: list[Annotated[ServerItemSection, Field(discriminator="itemType")]]
    banner: SRL | None = None


class ServerItemDetails(BaseModel):
    item: ServerItem
    description: str | None = None
    actions: list[ServerForm]
    hasCommunity: bool
    leaderboards: list[ServerItemLeaderboard]
    sections: list[Annotated[ServerItemSection, Field(discriminator="itemType")]]

class ServerSubmitItemCommunityCommentActionResponse(BaseModel):
    key: str
    hashes: list[str]
    shouldUpdateCommunity: bool | None = None
    shouldUpdateComments: bool | None = None
    shouldNavigateCommentsToPage: int | None = None

class ServerItemCommunityInfo(BaseModel):
    actions: list[ServerForm]
    topComments: list[ServerItemCommunityComment]

class ServerSubmitItemActionResponse(BaseModel):
    key: str
    hashes: list[str]
    shouldUpdateItem: bool | None = None
    shouldRemoveItem: bool | None = None
    shouldNavigateToItem: str | None = None

class ServerItemList(BaseModel):
    pageCount: int
    cursor: str | None = None
    items: list[ServerItem]
    searches: list[ServerForm] | None = None
    quickSearchValues: str | None = None

class ServerConfiguration(BaseModel):
    options: list[ServerOption]

class ServerInfo(BaseModel):
    title: str
    description: str | None = None
    buttons: list[ServerInfoItemButton]
    configuration: ServerConfiguration
    banner: SRL | None

class ServerAuthenticateResponse(BaseModel):
    session: str
    expiration: int | float

class ServerSubmitLevelResultResponse(BaseModel):
    key: str
    hashes: list[str]

class ServerItemLeaderboardDetails(BaseModel):
    topRecords: list[ServerItemLeaderboardRecord]
    
class ServerItemLeaderboardRecordList(BaseModel):
    pageCount: int
    cursor: str | None = None
    records: list[ServerItemLeaderboardRecord]

class ServerItemLeaderboardRecordDetails(BaseModel):
    replays: list[ReplayItem]

class ServerResultInfo(BaseModel):
    submits: list[ServerForm] | None = None