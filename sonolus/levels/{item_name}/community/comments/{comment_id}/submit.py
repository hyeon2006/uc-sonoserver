from fastapi import APIRouter
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.models.sonolus.submit import GenericActionRequest
from helpers.models.sonolus.response import ServerSubmitItemCommunityCommentActionResponse

router = APIRouter()

@router.post("/", response_model=ServerSubmitItemCommunityCommentActionResponse)
async def main(
    request: SonolusRequest,
    item_name: str,
    comment_id: int,
    data: GenericActionRequest,
):
    locale = request.state.loc
    auth = request.headers.get("Sonolus-Session")

    parsed_data = data.parse()

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=locale.not_logged_in,
        )
    
    if parsed_data.type not in ["delete"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
        )
    
    delete_response = await request.app.api.delete_comment(item_name, comment_id).send(auth)

    if delete_response.status != 200:
        raise HTTPException(status_code=delete_response.status, detail=locale.unknown_error)

    if delete_response.data.mod and not delete_response.data.owner:
        send_notification_response = await request.app.api.send_notification(
            title="Comment Deleted", 
            user_id=delete_response.data.commenter,
            content=f"#COMMENT_DELETED\n{delete_response.data.content}"
        ).send(auth)

        if send_notification_response.status != 200:
            raise HTTPException(
                status_code=send_notification_response.status, detail=locale.not_mod
            )

    return ServerSubmitItemCommunityCommentActionResponse(
        key="",
        hashes=[],
        shouldUpdateComments=True
    )
