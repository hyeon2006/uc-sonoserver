from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.sonolus_typings import ItemType

from helpers.models.sonolus.submit import ServerSubmitCommentActionRequest
from helpers.models.api.comments import CommentRequest
from helpers.models.sonolus.response import ServerSubmitItemCommunityCommentActionResponse

router = APIRouter()

from locales.locale import Locale

import aiohttp


@router.post("/", response_model=ServerSubmitItemCommunityCommentActionResponse)
async def main(
    request: SonolusRequest,
    item_name: str,
    data: ServerSubmitCommentActionRequest,
):
    try:
        locale = request.state.loc
    except AssertionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    auth = request.headers.get("Sonolus-Session")

    parsed_data = data.parse()

    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=locale.not_logged_in,
        )

    type = parsed_data.type
    if type not in ["comment"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
        )
    
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.post(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/comment/",
            json=CommentRequest(content=parsed_data.content).model_dump(),
        ) as req:
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=locale.unknown_error
                )

    return ServerSubmitItemCommunityCommentActionResponse(
        key="",
        hashes=[],
        shouldUpdateComments=True
    )
