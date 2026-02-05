from typing import Literal
from fastapi import APIRouter
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.data_compilers import compile_static_posts_list
from helpers.models.sonolus.response import ServerItemDetails

router = APIRouter()

@router.get("/", response_model=ServerItemDetails)
async def main(request: SonolusRequest, item_name: str):
    locale = request.state.loc
    item_data = None
    auth = request.headers.get("Sonolus-Session")

    if item_name.startswith("notification-"):
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
    else:
        data = await request.app.run_blocking(
            compile_static_posts_list, request.app.base_url
        )

        extended_item_data = next((i for i in data if i["name"] == item_name), None)
        desc = extended_item_data.description

        item_data = extended_item_data.to_post_item()

    return ServerItemDetails(
        item=item_data,
        description=desc,
        actions=[],
        hasCommunity=False,
        leaderboards=[],
        sections=[]
    )
