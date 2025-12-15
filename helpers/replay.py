# Not in chart-backend because all of the engines are here

from core import SonolusRequest
from fastapi import HTTPException, status
from pydantic import BaseModel
import hmac
import base64
import time
import hashlib
import json
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

    match option["type"]:
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

def validate_replay_config(compressed_replay_config: bytes, engine_name: str) -> AdditionalReplayInfo:
    replay_config = json.load(gzip.GzipFile(fileobj=BytesIO(compressed_replay_config)))
    additional_info = AdditionalReplayInfo()

    for option_value, (option_name, option_validator) in zip(replay_config["options"], engine_settings[engine_name].items()):
        if not option_validator(option_value):
            raise ValueError(f"invalid value for {option_name}: {option_value}") # TODO: raise httpexc and localize?
        
        match option_name:
            case "#SPEED":
                additional_info.speed = float(option_value)

    return additional_info

UPLOAD_KEY_EXPIRE_TIME = 180

class UploadKeyData(BaseModel):
    user_id: str
    expires_at: int
    level_name: str
    data_hash: str
    configuration_hash: str 
    engine_name: str
    display_name: str

def generate_upload_key(
    sonolus_id: str, 
    level_name: str, 
    data_hash: str, 
    configuration_hash: str, 
    engine_name: str, 
    display_name: str,
    request: SonolusRequest
) -> str:
    upload_key_data = UploadKeyData(
        user_id=sonolus_id,
        expires_at=int(time.time() + UPLOAD_KEY_EXPIRE_TIME),
        level_name=level_name,
        data_hash=data_hash,
        configuration_hash=configuration_hash,
        engine_name=engine_name,
        display_name=display_name
    )

    encoded_key = base64.urlsafe_b64encode(upload_key_data.model_dump_json().encode())

    signature = hmac.new(
        request.app.config["upload-token-sig-key"].encode(), encoded_key, hashlib.sha256
    ).hexdigest()

    return f"{encoded_key.decode()}.{signature}"

def verify_upload_key(upload_key: str, request: SonolusRequest) -> UploadKeyData:
    encoded_data, signature = upload_key.rsplit(".", 1)

    decoded_data = UploadKeyData.model_validate_json(
        base64.urlsafe_b64decode(encoded_data).decode()
    )

    if decoded_data.expires_at > time.time():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired upload token.")

    recalculated_signature = hmac.new(
        request.app.config["upload-token-sig-key"].encode(), encoded_data.encode(), hashlib.sha256
    ).hexdigest()

    if recalculated_signature != signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid upload token.")
    
    return decoded_data

# TODO: check config_overrides