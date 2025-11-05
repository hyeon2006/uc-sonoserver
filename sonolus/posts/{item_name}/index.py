import base64, asyncio

from urllib.parse import parse_qs
from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.data_compilers import compile_static_posts_list
from helpers.sonolus_typings import ItemType
from helpers.models.sonolus.response import ServerItemDetails
from helpers.models.api.notifications import Notification

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_item_uwu, handle_uwu

import aiohttp


@router.get("/")
async def main(request: SonolusRequest, item_type: ItemType, item_name: str):
    locale: Loc = request.state.loc
    item_data = None
    auth = request.headers.get("Sonolus-Session")

    if item_name.startswith("notification-"):
        if not auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=locale.not_logged_in,
            )
        headers = {"authorization": auth}
        async with aiohttp.ClientSession(headers=headers) as cs:
            async with cs.get(
                request.app.api_config["url"]
                + f"/api/accounts/notifications/{item_name.removeprefix('notification-')}/"
            ) as req:
                if req.status != 200:
                    raise HTTPException(
                        status_code=req.status, detail=locale.not_found
                    )
                data = Notification.model_validate(await req.json())
        item_data, desc = data.to_post(request)
    else:
        item_data = await request.app.run_blocking(
            compile_static_posts_list, request.app.base_url
        )

    return ServerItemDetails(
        item=item_data,
        description=desc,
        actions=[],
        hasCommunity=False,
        leaderboards=[],
        sections=[]
    )
