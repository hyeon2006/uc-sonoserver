import asyncio

from typing import List

from fastapi import APIRouter, Request
from fastapi import HTTPException, status
from core import SonolusRequest
from helpers.sonolus_typings import ItemType

router = APIRouter()

from locales.locale import Loc


@router.post("/")
async def main(request: SonolusRequest):
    locale = request.state.loc

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=locale.use_website_to_upload("https://untitledcharts.com"),
    )