import base64, decimal
from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.sonolus_typings import ItemType

from pydantic import BaseModel

from urllib.parse import parse_qs, urlencode

router = APIRouter()

from locales.locale import Loc

import aiohttp


class ServerSubmitItemActionRequest(BaseModel):
    values: str


@router.post("/")
async def main(
    request: SonolusRequest,
    item_name: str,
    data: ServerSubmitItemActionRequest,
):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")

    parsed = parse_qs(data.values)
    flattened_data = {k: v[0] for k, v in parsed.items()}

    if not item_name.startswith("uploaded"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
        )

    old_values = item_name.split("_", 1)
    if len(data.values) > 500 or len(item_name) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="why so long"
        )
    if len(old_values) == 1:
        old_values = ""
    else:
        try:
            old_values = base64.urlsafe_b64decode(old_values[1].encode()).decode()
        except:
            old_values = ""
    new_values = parse_qs(data.values)
    if old_values:
        old_values_list = parse_qs(old_values)
        for key in old_values_list:
            if key in new_values:
                old_values_list[key] = new_values[key]
            else:
                old_values_list[key] = old_values_list[key]
        for key in new_values:
            if key not in old_values_list:
                old_values_list[key] = new_values[key]
        updated_old_values = urlencode(old_values_list, doseq=True)
    else:
        updated_old_values = urlencode(new_values, doseq=True)
    resp = {
        "key": "",
        "hashes": [],
        "shouldNavigateToItem": f"uploaded_{base64.urlsafe_b64encode(updated_old_values.encode()).decode()}",
    }

    return resp
