from core import SonolusRequest
from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from fastapi import HTTPException, status
from locales.locale import Loc
import decimal

def is_valid_constant(c: str):
    try:
        if not isinstance(c, str):
            return False
        d = decimal.Decimal(c)
        if not (-1000 < d < 1000):
            return False
        # precision check: less than 4 digits after decimal (excluding trailing zeros)
        if "." in c:
            dec_part = c.split(".")[1].rstrip("0")
            if len(dec_part) >= 4:
                return False
        return True
    except (decimal.InvalidOperation, ValueError):
        return False

async def rerate(auth: str, request: SonolusRequest, item_name: str, constant: str, locale: Loc) -> ServerSubmitItemActionResponse:
    if not is_valid_constant(constant):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=locale.invalid_constant,
        )
    
    response = await request.app.api.rerate_chart(item_name, constant).send(auth)
    if response.status != 200:
        raise HTTPException(
            status_code=response.status, detail=locale.not_mod_or_owner
        )
            
    return ServerSubmitItemActionResponse(
        key="",
        hashes=[],
        shouldUpdateItem=True
    )