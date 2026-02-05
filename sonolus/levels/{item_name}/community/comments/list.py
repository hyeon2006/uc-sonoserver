from fastapi import APIRouter, Query
from fastapi import HTTPException

from core import SonolusRequest

from helpers.models.sonolus.response import ServerItemCommunityCommentList
from helpers.models.sonolus.options import ServerForm

router = APIRouter()

@router.get("/", response_model=ServerItemCommunityCommentList)
async def main(
    request: SonolusRequest, 
    item_name: str,
    page: int = Query(0, ge=0)
):
    locale = request.state.loc
    auth = request.headers.get("Sonolus-Session")

    response = await request.app.api.get_comments(item_name, page).send(auth)
    page_count = response.data.pageCount
    if page > page_count or page < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                locale.invalid_page_plural(page, page_count)
                if page_count != 1
                else locale.invalid_page_singular(page, page_count)
            ),
        )
    elif page_count == 0:
        raise HTTPException(status_code=400, detail=locale.not_found)

    return ServerItemCommunityCommentList(
        pageCount=page_count,
        comments=await request.app.run_blocking(
            response.data.to_server_item_community_comments,
            request
        )
    )
