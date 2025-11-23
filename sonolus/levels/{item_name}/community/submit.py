from fastapi import APIRouter
from fastapi import HTTPException, status

from core import SonolusRequest

from helpers.models.sonolus.submit import ServerSubmitCommentActionRequest
from helpers.models.sonolus.response import ServerSubmitItemCommunityCommentActionResponse

router = APIRouter()


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

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=locale.not_logged_in,
        )

    if parsed_data.type not in ["comment"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
        )
    
    response = await request.app.api.send_comment(item_name, parsed_data.content).send(auth)

    if response.status != 200:
        raise HTTPException(
            status_code=response.status, detail=locale.unknown_error
        )

    return ServerSubmitItemCommunityCommentActionResponse(
        key="",
        hashes=[],
        shouldUpdateComments=True
    )
