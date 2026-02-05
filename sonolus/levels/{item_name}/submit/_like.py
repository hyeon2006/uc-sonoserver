from core import SonolusRequest
from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from fastapi import HTTPException
from typing import Literal
from locales.locale import Loc

async def like(auth: str, request: SonolusRequest, item_name: str, type: Literal["like", "unlike"], locale: Loc) -> ServerSubmitItemActionResponse:
    response = await request.app.api.like_chart(item_name, type).send(auth)

    if response.status != 200:
        raise HTTPException(
            status_code=response.status, detail=locale.unknown_error
        )
            
    return ServerSubmitItemActionResponse(
        key="",
        hashes=[],
        shouldUpdateItem=True
    )