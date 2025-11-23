from fastapi import APIRouter
from fastapi import HTTPException, status

from core import SonolusRequest
from . import _like, _delete, _rerate, _staff_pick, _visibility

from helpers.models.sonolus.submit import ServerSubmitLevelActionRequest
from helpers.models.sonolus.response import ServerSubmitItemActionResponse

router = APIRouter()


@router.post("/", response_model=ServerSubmitItemActionResponse)
async def main(
    request: SonolusRequest,
    item_name: str,
    data: ServerSubmitLevelActionRequest,
):
    locale = request.state.loc
    auth = request.headers.get("Sonolus-Session")

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=locale.not_logged_in,
        )

    flattened_data = data.parse()
    
    match flattened_data.type:
        case "like" | "unlike":
            return await _like.like(auth, request, item_name, flattened_data.type, locale)
        case "delete":
            return await _delete.delete(auth, request, item_name, locale)
        case "visibility":
            return await _visibility.visibility(auth, request, item_name, flattened_data.visibility, locale)
        case "rerate":
            return await _rerate.rerate(auth, request, item_name, flattened_data.constant, locale)
        case "staff_pick_add" | "staff_pick_delete":
            return await _staff_pick.staff_pick(auth, request, item_name, flattened_data.type, locale)
        case _:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
            )