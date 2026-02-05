from core import SonolusRequest
from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from fastapi import HTTPException
from locales.locale import Loc
from typing import Literal

async def staff_pick(auth: str, request: SonolusRequest, item_name: str, type: Literal["staff_pick_add", "staff_pick_delete"], locale: Loc) -> ServerSubmitItemActionResponse:
    response = await request.app.api.staff_pick_chart(item_name, True if type == "staff_pick_add" else False).send(auth)

    if response.status != 200:
        raise HTTPException(
            status_code=response.status, detail=locale.not_mod
        )
            
    return ServerSubmitItemActionResponse(
        key="",
        hashes=[],
        shouldUpdateItem=True
    )