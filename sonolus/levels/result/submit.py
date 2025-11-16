from fastapi import APIRouter, Request
from fastapi import HTTPException, status
from core import SonolusRequest
from helpers.sonolus_typings import ItemType
from helpers.models.sonolus.item import ReplayItem
import aiohttp
import json

router = APIRouter()

from locales.locale import Loc

# class ServerSubmitLevelResultRequest(BaseModel):
#     replay: ReplayItem
#     values: str # "type=replay"

# class ServerSubmitLevelResultResponse(BaseModel):
#     key: str
#     hashes: list[str]

# TODO

@router.post("/")
async def main(request: SonolusRequest, item_type: ItemType, data: ServerSubmitLevelResultRequest):
    locale: Loc = request.state.loc

    if item_type != "levels":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.item_type_not_found(item_type)
        )
    
    auth = request.headers.get("Sonolus-Session")

    async with aiohttp.ClientSession(headers=({"authorization": auth} if auth else None)) as session: # TODO: shared ClientSession
        async with session.get(
            request.app.api_config["url"]
            + f"/api/accounts/generate_upload_token/",
            params={"hashes": json.dumps({
                "data": data.replay
            })}
        ) as req:
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=locale.unknown_error
                )

            return ServerSubmitLevelResultResponse(
                key=await req.text(),
                hashes=[

                ]
            )