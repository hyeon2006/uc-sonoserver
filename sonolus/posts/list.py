from fastapi import APIRouter, Query
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.paginate import list_to_pages
from helpers.models.sonolus.response import ServerItemList

router = APIRouter()

from helpers.owoify import handle_item_uwu

type_func = type


@router.get("/")
async def main(
    request: SonolusRequest,
    page: int = Query(0, ge=0),
):
    locale = request.state.loc
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")

    if auth:
        response = await request.app.api.get_notifications(only_unread=False).send(auth)
        notifs = response.data.to_posts(request)
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

    return ServerItemList(
        pageCount=len(pages),
        items=page_data
    )
