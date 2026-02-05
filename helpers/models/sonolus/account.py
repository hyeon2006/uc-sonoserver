from pydantic import BaseModel
from typing import Literal

class ServiceUserProfile(BaseModel):
    id: str  # ServiceUserId... is just a string.
    handle: str
    name: str
    avatarType: str
    avatarForegroundType: str
    avatarForegroundColor: str
    avatarBackgroundType: str
    avatarBackgroundColor: str
    bannerType: str
    aboutMe: str
    favorites: list[str]

class ServerAuthenticateRequest(BaseModel):
    type: str
    address: str
    time: int
    userProfile: ServiceUserProfile

class ServerAuthenticateExternalRequest(BaseModel):
    type: str
    url: str
    time: int
    userProfile: ServiceUserProfile

class ServiceUserProfileWithType(ServiceUserProfile):
    type: Literal["game", "external"]