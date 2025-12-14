from typing import Literal, Annotated
from pydantic import BaseModel, Field
from helpers.models.sonolus.misc import SIL
from helpers.sonolus_typings import Icon, ItemType, Text


class ServerCollectionItemOption(BaseModel):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["collectionItem"] = "collectionItem"
    itemType: ItemType

class DumpDefAliasMixin(BaseModel):
    def model_dump(self, **kwargs):
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)

class ServerTextOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["text"] = "text"
    default: str = Field(validation_alias="def", serialization_alias="def")
    placeholder: Text | str
    limit: int
    shortcuts: list[str]

class ServerTextAreaOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["textArea"] = "textArea"
    default: str = Field(validation_alias="def", serialization_alias="def")
    placeholder: Text | str
    limit: int
    shortcuts: list[str]

class ServerSliderOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["slider"] = "slider"
    default: int | float = Field(validation_alias="def", serialization_alias="def")
    min: int | float
    max: int | float
    step: int | float
    unit: Text | str | None = None

class ServerToggleOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["toggle"] = "toggle"
    default: bool = Field(validation_alias="def", serialization_alias="def")

class ServerOption_Value(BaseModel):
    name: str
    title: Text | str

class ServerSelectOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["select"] = "select"
    default: str = Field(validation_alias="def", serialization_alias="def")
    values: list[ServerOption_Value]

class ServerMultiOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["multi"] = "multi"
    default: list[bool] = Field(validation_alias="def", serialization_alias="def")
    values: list[ServerOption_Value]

class ServerServerItemOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["serverItem"] = "serverItem"
    itemType: ItemType
    default: SIL | None = Field(None, validation_alias="def", serialization_alias="def")
    allowOtherServers: bool

class ServerServerItemsOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["serverItems"] = "serverItems"
    itemType: ItemType
    default: list[SIL] = Field(validation_alias="def", serialization_alias="def")
    allowOtherServers: bool
    limit: int

class ServerCollectionItemOption(BaseModel):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["collectionItem"] = "collectionItem"
    itemType: ItemType

class ServerFileOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["file"] = "file"
    default: str = Field(validation_alias="def", serialization_alias="def")

ServerOption = (
    ServerTextOption
    | ServerTextAreaOption
    | ServerSliderOption
    | ServerToggleOption
    | ServerSelectOption
    | ServerMultiOption
    | ServerServerItemOption
    | ServerServerItemsOption
    | ServerCollectionItemOption
    | ServerFileOption
)

class ServerForm(BaseModel):
    type: str
    title: Text | str
    icon: Icon | str | None = None
    description: str | None = None
    help: str | None = None
    requireConfirmation: bool
    options: list[Annotated[ServerOption, Field(discriminator="type")]]