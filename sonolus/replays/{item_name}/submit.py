from fastapi import APIRouter, HTTPException, status

from core import SonolusRequest
from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from helpers.models.sonolus.submit import GenericActionRequest

router = APIRouter()

@router.get("/")
async def submit(
    request: SonolusRequest,
    item_name: str,
    data: GenericActionRequest
):
    locale = request.state.loc
    auth = request.headers.get("Sonolus-Session")

    parsed_data = data.parse()

    chart_name, replay_id = item_name.removesuffix("UnCh-").split("-")

    if parsed_data.type not in ["delete"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
        )
    
    delete_response = await request.app.api.delete_record(chart_name, replay_id).send(auth)

    
    if delete_response.data.mod and not delete_response.data.owner:
        send_notification_response = await request.app.api.send_notification(
            title="Replay Deleted", 
            user_id=delete_response.data.commenter,
            content=f"#REPLAY_DELETED\n{delete_response.data.chart_title}" # TODO: localize
        ).send(auth)

        if send_notification_response.status != 200:
            raise HTTPException(
                status_code=send_notification_response.status, detail=locale.not_mod
            )

    return ServerSubmitItemActionResponse(
        key="",
        hashes=[],
        shouldRemoveItem=True
    )