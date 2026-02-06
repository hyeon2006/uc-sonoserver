import base64
from fastapi import APIRouter
from fastapi import HTTPException, status

from core import SonolusRequest

from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from helpers.models.sonolus.submit import ServerSubmitPlaylistActionRequest

from urllib.parse import urlencode

router = APIRouter()


@router.post("/", response_model=ServerSubmitItemActionResponse)
async def main(
    request: SonolusRequest,
    item_name: str,
    data: ServerSubmitPlaylistActionRequest,
) -> ServerSubmitItemActionResponse:
    locale = request.state.loc

    if not item_name.startswith("uploaded"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
        )

    if len(item_name) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="why so long"
        )

    old_values_list = item_name.split("_", maxsplit=1)
    old_values = old_values_list[1] if len(old_values_list) == 2 else ""

    updated_old_values = urlencode(
        ServerSubmitPlaylistActionRequest(values=old_values)
        .parse(request)
        .model_copy(
            update=data
                .parse(request, plain_json=True)
                .model_dump()
        )
        .model_dump()
    )

    return ServerSubmitItemActionResponse(
        key="",
        hashes=[],
        shouldNavigateToItem=f"uploaded_{base64.urlsafe_b64encode(updated_old_values.encode()).decode()}",
    )
