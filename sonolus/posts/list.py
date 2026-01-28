from typing import Literal
from fastapi import APIRouter, Query
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.data_compilers import compile_static_posts_list, sort_posts_by_newest
from helpers.models.sonolus.item_section import PostItemSection
from helpers.paginate import list_to_pages
from helpers.models.sonolus.response import ServerItemList

router = APIRouter()

from helpers.owoify import handle_item_uwu

type_func = type


@router.get("/")
async def main(
    request: SonolusRequest,
    type: Literal["announcements", "notifications"] | str,
    page: int = Query(0, ge=0),
):
    locale = request.state.loc
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")

    match type:
        case "announcements":
            data = await request.app.run_blocking(
                compile_static_posts_list, request.app.base_url
            )

            data = sort_posts_by_newest(data)
            data = handle_item_uwu(data, request.state.localization, uwu_level)

        case "notifications":
            if auth:
                response = await request.app.api.get_notifications(only_unread=False).send(auth)
                data = response.data.to_posts(request)
            if not (auth and data):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=locale.notification.none_past,
                )

    pages = list_to_pages(data, request.app.get_items_per_page("posts"))
    if len(pages) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=locale.items_not_found(type)
        )
    
    try:
        items = pages[page]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="hi stop hitting our api thanks",
        )

    return ServerItemList(
        pageCount=len(pages),
        items=items
    )
