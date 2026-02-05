from fastapi import HTTPException
from core import SonolusRequest
from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from locales.locale import Loc
from typing import Literal

async def visibility(auth: str, request: SonolusRequest, item_name: str, visibility: Literal["UNLISTED", "PRIVATE", "PUBLIC"], locale: Loc) -> ServerSubmitItemActionResponse:
    change_visibility_response = await request.app.api.change_chart_visibility(item_name, visibility).send(auth)

    if change_visibility_response.status != 200:
        raise HTTPException(
            status_code=change_visibility_response.status, detail=locale.not_mod_or_owner
        )
        
    if (
        visibility != "PUBLIC"
        and change_visibility_response.data.mod
        and not change_visibility_response.data.owner
    ):
        send_notification_response = await request.app.api.send_notification(
            title="Chart Visibility Update",
            user_id=change_visibility_response.data.author,
            content=f"#CHART_VISIBILITY_CHANGED\n{visibility}\n{change_visibility_response.data.title}"
        ).send(auth)

        if send_notification_response.status != 200:
            raise HTTPException(
                status_code=send_notification_response.status, detail=locale.not_mod
            )
                
    return ServerSubmitItemActionResponse(
        key="",
        hashes=[],
        shouldUpdateItem=True
    )