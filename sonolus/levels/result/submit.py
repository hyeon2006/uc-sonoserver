from fastapi import APIRouter, HTTPException, status
from core import SonolusRequest

from helpers.models.sonolus.response import ServerSubmitLevelResultResponse
from helpers.models.sonolus.submit import ServerSubmitLevelResultRequest
import helpers.replay as replay

router = APIRouter()

@router.post("/")
async def main(request: SonolusRequest, data: ServerSubmitLevelResultRequest):
    locale = request.state.loc
    
    auth = request.headers.get("Sonolus-Session")

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=locale.not_logged_in,
        )

    response = await request.app.api.get_account().send(auth)

    return ServerSubmitLevelResultResponse(
        key=replay.generate_upload_key(
            response.data.sonolus_id,
            data.replay.level.name,
            data.replay.data.hash,
            data.replay.configuration.hash,
            request.state.engine,
            f"{response.data.sonolus_id}#{response.data.sonolus_handle}",
            request
        ),
        hashes=[
            data.replay.data.hash, data.replay.configuration.hash
        ]
    )
