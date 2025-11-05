import base64, decimal
from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from core import SonolusRequest
from . import _like, _delete, _rerate, _staff_pick, _visibility

from helpers.sonolus_typings import ItemType
from helpers.models.sonolus.submit import ServerSubmitLevelActionRequest
from helpers.models.sonolus.response import ServerSubmitItemActionResponse

from urllib.parse import parse_qs, urlencode

router = APIRouter()

from locales.locale import Loc


@router.post("/", response_model=ServerSubmitItemActionResponse)
async def main(
    request: SonolusRequest,
    item_name: str,
    data: ServerSubmitLevelActionRequest,
):
    locale: Loc = request.state.loc
    auth = request.headers.get("Sonolus-Session")

    flattened_data = data.parse()

    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=locale.not_logged_in,
        )
    
    match type:
        case "like" | "unlike":
            return await _like.like(headers, request, item_name, type, locale)
        case "delete":
            return await _delete.delete(headers, request, item_name, locale)
        case "visibility":
            return await _visibility.visibility(headers, request, item_name, flattened_data.visibility, locale)
        case "rerate":
            return await _rerate.rerate(headers, request, item_name, flattened_data.constant, locale)
        case "staff_pick_add" | "staff_pick_delete":
            return await _staff_pick.staff_pick(headers, request, item_name, type, locale)
        case _:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
            )