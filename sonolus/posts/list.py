import asyncio

from fastapi import APIRouter, Request, Query
from fastapi import HTTPException, status


import aiohttp

from core import SonolusRequest
from helpers.paginate import list_to_pages
from helpers.models.api.notifications import NotificationList

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_item_uwu

type_func = type


@router.get("/")
async def main(
    request: SonolusRequest,
    page: int = Query(0, ge=0),
):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")

    if auth:
        headers = {request.app.auth_header: request.app.auth}
        headers["authorization"] = auth
        async with aiohttp.ClientSession(headers=headers) as cs:
            async with cs.get(
                request.app.api_config["url"] + f"/api/accounts/notifications/",
                params={"only_unread": 0},
            ) as req:
                response = NotificationList.model_validate(await req.json())
        notifs = response.to_posts()
    if not (auth and notifs):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=locale.notification.none_past,
        )

    pages = list_to_pages(notifs, request.app.get_items_per_page("posts"))
    if len(pages) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=locale.items_not_found("posts")
        )
    try:
        page_data = pages[page]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="hi stop hitting our api thanks",
        )
    page_data = handle_item_uwu(page_data, request.state.localization, uwu_level)
    return {
        "pageCount": len(pages),
        "items": page_data,
    }
