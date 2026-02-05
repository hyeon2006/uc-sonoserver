from typing import TypedDict
import yaml

ConfigTypeServer = TypedDict(
    "ConfigTypeServer",
    {
        "port": int,
        "base-url": str,
        "force-https": bool,
        "debug": bool
    }
)

ItemsPerPage = TypedDict(
    "ItemsPerPage",
    {
        "default": int,
        "engines": int
    }
)

ConfigTypeSonolus = TypedDict(
    "ConfigTypeSonolus",
    {
        "required-client-version": str,
        "items-per-page": ItemsPerPage,
        "name": str,
        "description": str,
        "upload-token-sig-key": str
    }
)

ConfigTypeAPI = TypedDict(
    "ConfigTypeAPI",
    {
        "url": str,
        "auth": str,
        "auth-header": str
    }
)

ConfigType = TypedDict(
    "ConfigType",
    {
        "server": ConfigTypeServer,
        "sonolus": ConfigTypeSonolus,
        "api": ConfigTypeAPI
    }
)

def get_config() -> ConfigType:
    with open("config.yml", "r") as f:
        return yaml.load(f, yaml.Loader)