from core import SonolusRequest
from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from fastapi import HTTPException
from locales.locale import Loc

async def delete(auth: str, request: SonolusRequest, item_name: str, locale: Loc) -> ServerSubmitItemActionResponse:
    delete_response = await request.app.api.delete_chart(item_name).send(auth)
    
    if delete_response.status != 200:
        raise HTTPException(
            status_code=delete_response.status, detail=locale.not_admin_or_owner
        )

    if delete_response.data.admin and not delete_response.data.owner:
        send_notification_response = await request.app.api.send_notification(
            title="Chart Deleted",
            user_id=delete_response.data.author,
            content=f"#CHART_DELETED\n{delete_response.data.title}"
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