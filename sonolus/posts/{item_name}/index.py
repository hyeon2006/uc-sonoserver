from typing import Literal
from fastapi import APIRouter
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.data_compilers import compile_static_posts_list
from helpers.models.sonolus.response import ServerItemDetails

router = APIRouter()

@router.get("/")
async def main(request: SonolusRequest, item_name: str, type: Literal["announcements", "notifications"] | str):
    locale = request.state.loc
    item_data = None
    auth = request.headers.get("Sonolus-Session")

    match type:
        case "announcements":
            item_data = await request.app.run_blocking(
                compile_static_posts_list, request.app.base_url
            )
        case "notifications": 
            if not auth:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=locale.not_logged_in,
                )
        
            response = await request.app.api.get_notification(item_name).send(auth)

            if response.status != 200:
                raise HTTPException(
                    status_code=response.status, detail=locale.not_found
                )

            item_data, desc = response.data.to_post(request)
        case _:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=locale.item_type_not_found(type))

    return ServerItemDetails(
        item=item_data,
        description=desc,
        actions=[],
        hasCommunity=False,
        leaderboards=[],
        sections=[]
    )
