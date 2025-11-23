from fastapi import APIRouter
from fastapi import HTTPException
from core import SonolusRequest
import aiohttp
import json

router = APIRouter()

# class ServerSubmitLevelResultRequest(BaseModel):
#     replay: ReplayItem
#     values: str # "type=replay"

# class ServerSubmitLevelResultResponse(BaseModel):
#     key: str
#     hashes: list[str]

# TODO (sonoserv)

@router.post("/")
async def main(request: SonolusRequest, data: ServerSubmitLevelResultRequest):
    locale = request.state.loc
    
    auth = request.headers.get("Sonolus-Session")

    async with aiohttp.ClientSession(headers=({"authorization": auth} if auth else None)) as session:
        async with session.get(
            request.app.api_config["url"]
            + f"/api/accounts/generate_upload_token/", # this needs to go
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