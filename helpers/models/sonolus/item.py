from pydantic import BaseModel
from typing import Literal, TypeAlias
from helpers.models.sonolus.misc import Tag, SRL
from helpers.models.sonolus.options import ServerForm

class BackgroundItem(BaseModel):
    name: str
    source: str | None = None
    version: Literal[2] = 2
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    thumbnail: SRL
    data: SRL
    image: SRL
    configuration: SRL


class ParticleItem(BaseModel):
    name: str
    source: str | None = None
    version: Literal[3] = 3
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    thumbnail: SRL
    data: SRL
    texture: SRL


class EffectItem(BaseModel):
    name: str
    source: str | None = None
    version: Literal[5] = 5
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    thumbnail: SRL
    data: SRL
    audio: SRL


class SkinItem(BaseModel):
    name: str
    source: str | None = None
    version: Literal[4] = 4
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    thumbnail: SRL
    data: SRL
    texture: SRL


class EngineItem(BaseModel):
    name: str
    version: Literal[13] = 13
    title: str
    subtitle: str
    source: str | None = None
    author: str
    tags: list[Tag]
    description: str | None = None

    skin: SkinItem
    background: BackgroundItem
    effect: EffectItem
    particle: ParticleItem

    thumbnail: SRL
    playData: SRL
    watchData: SRL
    previewData: SRL
    tutorialData: SRL
    rom: SRL | None = None
    configuration: SRL


class PostItem(BaseModel):
    name: str
    source: str | None = None
    version: Literal[1] = 1
    title: str
    time: int
    author: str
    tags: list[Tag]
    thumbnail: SRL | None = None


class UseItem(BaseModel):
    useDefault: bool
    item: SkinItem | BackgroundItem | EffectItem | ParticleItem | None = None


class LevelItem(BaseModel):
    name: str
    source: str | None = None
    version: Literal[1] = 1
    rating: int
    title: str
    artists: str
    author: str
    tags: list[Tag] = None
    engine: EngineItem
    useSkin: UseItem[SkinItem]
    useBackground: UseItem[BackgroundItem]
    useEffect: UseItem[EffectItem]
    useParticle: UseItem[ParticleItem]
    cover: SRL
    bgm: SRL
    preview: SRL | None = None
    data: SRL


class PlaylistItem(BaseModel):
    name: str
    source: str | None = None
    version: Literal[1] = 1
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    levels: list[LevelItem]
    thumbnail: SRL | None = None


class RoomItem(BaseModel):
    name: str
    title: str
    subtitle: str
    master: str
    tags: list[Tag]
    cover: SRL | None = None
    bgm: SRL | None = None
    preview: SRL | None = None


class ReplayItem(BaseModel):
    name: str
    source: str | None = None
    version: Literal[1] = 1
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    level: LevelItem
    data: SRL
    configuration: SRL


ServerItem: TypeAlias = (
    PostItem
    | RoomItem
    | SkinItem
    | BackgroundItem
    | ParticleItem
    | EffectItem
    | RoomItem
    | PlaylistItem
    | ReplayItem
    | LevelItem
    | EngineItem
)

class ServerItemCommunityComment(BaseModel):
    name: str
    author: str
    time: int  # ms epoch
    content: str
    actions: list[ServerForm]

class ServerItemList(BaseModel):
    pageCount: int
    cursor: str | None = None
    items: list[ServerItem]
    searches: list[ServerForm] | None = None