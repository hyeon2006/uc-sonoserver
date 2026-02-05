from fastapi import APIRouter, HTTPException, Query, status

from core import SonolusRequest
from helpers.models.sonolus.response import ServerItemList
from helpers.owoify import handle_item_uwu

router = APIRouter()

@router.get("/", response_model=ServerItemList)
async def list(
    request: SonolusRequest,
    page: int = Query(0, ge=0),
    random: bool | None = Query(False)
):
    locale = request.state.loc

    response = await (
        request.app.api.get_random_leaderboard_records(limit=10)
        if random else
        request.app.api.get_public_leaderboard_records(page=page)
    ).send()

    page_count = response.data.pageCount
    if random:
        if len(response.data.data) == 10:
            page_count = (
                page + 2
            )  # always have one extra page, random will not run out and there may be duplicates
            # only if pageCount isn't 0 of course, and the api actually returned a full list (so there likely is more)
        else:
            page_count = int(len(response.data.data) != 0)

    if page > page_count or page < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                locale.invalid_page_plural(page, page_count)
                if page_count != 1
                else locale.invalid_page_singular(page, page_count)
            ),
        )
    elif page_count == 0 or len(response.data.data) == 0:
        raise HTTPException(
            status_code=400, detail=locale.items_not_found_search("replay")
        )
    
    return ServerItemList(
        pageCount=page_count,
        items=handle_item_uwu(
            await request.app.run_blocking(
                response.data.to_replay_items,
                request
            ),
            request.state.localization,
            request.state.uwu
        )
    )