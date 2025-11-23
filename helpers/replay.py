# Not in chart-backend because all of the engines are here

from os import listdir, path
from io import BytesIO
from typing import Callable
from pydantic import BaseModel
import gzip
import json

validator = Callable[[int | float], bool]
engine_settings: dict[str, dict[str, validator]] = {}

class AdditionalReplayInfo(BaseModel):
    speed: float | None = None

def get_validator(option: dict, engine_data: dict) -> validator:
    if option["name"] in engine_data.get("unrankable_options", []):
        return lambda value: value == option["def"]

    match option["name"]:
        case "slider":
            return lambda value: value >= option['min'] and value <= option['max']
        case "toggle":
            return lambda value: value in (0, 1)
        case "select":
            return lambda value: value >= 0 and value <= len(option["values"]) - 1
        case _:
            option_type = option["type"]
            raise ValueError(f"invalid option type: {option_type}")

for engine in listdir("files/engines"):
    if not path.isdir(path.join("files", "engines", engine)):
        continue

    with open(f"files/engines/{engine}/engine.json", "r", encoding="utf8") as file:
        engine_data: dict = json.load(file)

    if not engine_data.get("can_be_ranked", False):
        continue

    settings: dict[str, validator] = {}

    with gzip.open(f"files/engines/{engine}/EngineConfiguration", "rb") as file:
        engine_config: dict = json.load(file)

        for option in engine_config["options"]:
            settings[option["name"]] = get_validator(option, engine_data)

    engine_settings[engine_data["title"]] = settings

print("WARNING WARNING TODO (release) there are no unrankable options for nextrush and nextsekai yet")

def validate_replay_config(compressed_replay_config: bytes, engine_name: str) -> AdditionalReplayInfo:
    replay_config = json.load(gzip.GzipFile(fileobj=BytesIO(compressed_replay_config)))
    additional_info = AdditionalReplayInfo()

    for option_value, (option_name, option_validator) in zip(replay_config["options"], engine_settings[engine_name].items()):
        if not option_validator(option_value):
            raise ValueError(f"invalid value for {option_name}: {option_value}")
        
        match option_name:
            case "#SPEED":
                additional_info.speed = float(option_value)

    return additional_info