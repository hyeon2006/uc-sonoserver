from pydantic import BaseModel
from datetime import datetime

from helpers.models.api.charts import Chart
from helpers.models.sonolus.item import UserItem
from helpers.models.sonolus.misc import Tag

class Account(BaseModel):
    sonolus_id: str
    sonolus_handle: int
    sonolus_username: str
    created_at: datetime
    mod: bool | None = None
    admin: bool | None = None # XXX (backend): make these non-optional
    banned: bool | None = None
    unread_notifications: int

class AuthenticationData(BaseModel):
    session: str
    expiry: int

class PublicAccount(BaseModel):
    sonolus_id: str
    sonolus_handle: int
    sonolus_username: str
    mod: bool = False
    admin: bool = False
    banned: bool = False

    def to_user_item(self) -> UserItem:
        tags = []

        if self.admin:
            tags.append(Tag(title="#ADMIN", icon="crown"))
        elif self.mod:
            tags.append(Tag(title="#MODERATOR", icon="crown"))

        if self.banned:
            tags.append(Tag(title="#BANNED", icon="lock"))

        return UserItem(
            name=self.sonolus_id,
            title=self.sonolus_username,
            handle=str(self.sonolus_handle),
            tags=tags
        )

class UserProfile(BaseModel):
    account: PublicAccount
    charts: list[Chart]
    asset_base_url: str
