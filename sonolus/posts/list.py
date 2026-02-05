from typing import Literal
from fastapi import APIRouter, Query
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.data_compilers import compile_static_posts_list, sort_posts_by_newest
from helpers.paginate import list_to_pages
from helpers.models.sonolus.response import ServerItemList

router = APIRouter()

from helpers.owoify import handle_item_uwu


@router.get("/", response_model=ServerItemList)
async def main(
    request: SonolusRequest,
    page: int = Query(0, ge=0),
    post_type: Literal["all", "announcements", "notifications", None] = Query(None)
):
    locale = request.state.loc
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")

    data = []

    if post_type in ("all", "announcements", None):
        data.extend(
            [item.to_post_item() for item in await request.app.run_blocking(
                compile_static_posts_list, request.app.base_url
            )]
        )

    if post_type in ("all", "notifications", None):
        if not auth and post_type == "notifications":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if auth:
            response = await request.app.api.get_notifications(only_unread=False).send(auth)
            data.extend(response.data.to_posts(request))

    data = sort_posts_by_newest(data)
    data = handle_item_uwu(data, request.state.localization, uwu_level)

    pages = list_to_pages(data, request.app.get_items_per_page("posts"))
    if len(pages) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=locale.items_not_found("announcements")
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
