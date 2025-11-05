from core import SonolusRequest
from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from fastapi import HTTPException
from typing import Literal
from locales.locale import Loc
import aiohttp

async def like(headers: dict, request: SonolusRequest, item_name: str, type: Literal["like", "unlike"], locale: Loc) -> ServerSubmitItemActionResponse:
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.post(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/like/",
            json={"type": type},
        ) as req:
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=locale.unknown_error
                )
            
    return ServerSubmitItemActionResponse(
        key="",
        hashes=[],
        shouldUpdateItem=True
    )