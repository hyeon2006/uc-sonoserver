import asyncio

from fastapi import APIRouter, Query
from fastapi import HTTPException, status

from typing import Literal

import aiohttp

from core import SonolusRequest
from helpers.api_helpers import api_level_to_level_item
from helpers.models.api.levels import LevelList

router = APIRouter()

from helpers.owoify import handle_item_uwu

type_func = type


@router.get("/")
async def main(
    request: SonolusRequest,
    type: Literal["quick", "advanced"] = Query("quick"),
    page: int = Query(0, ge=0),
    staff_pick: Literal["default", "off", "true", "false", None] = Query("default"),
    min_rating: int | None = Query(None),
    max_rating: int | None = Query(None),
    tags: str | None = Query(None),
    min_likes: int | None = Query(None),
    max_likes: int | None = Query(None),
    min_comments: int | None = Query(None),
    max_comments: int | None = Query(None),
    liked_by: bool | None = Query(False),
    commented_on: bool | None = Query(False),
    title_includes: str | None = Query(None),
    description_includes: str | None = Query(None),
    author_includes: str | None = Query(None),
    artists_includes: str | None = Query(None),
    sort_by: Literal[
        "created_at",
        "published_at",
        "rating",
        "likes",
        "comments",
        "decaying_likes",
        "abc",
        "random",
    ] = Query("published_at"),
    sort_order: Literal["desc", "asc", None] = Query("desc"),
    level_status: Literal["PUBLIC", None] = Query(
        "PUBLIC"
    ),  # will only ever be PUBLIC here. anything else, go to playlists
    keywords: str | None = Query(None),
):
    locale = request.state.loc
    uwu_level = request.state.uwu
    searching = False
    auth = request.headers.get("Sonolus-Session")

    if type == "quick":
        params = {
            "type": type,
            "page": page,
            "meta_includes": keywords,
            "sort_by": "published_at",
            "staff_pick": {"off": None, "true": True, "false": False}[
                (
                    staff_pick
                    if staff_pick not in ["default", None]
                    else request.state.staff_pick
                )
            ],
        }
    else:
        params = {
            "type": type,
            "page": page if sort_by != "random" else 1,
            "staff_pick": {"off": None, "true": True, "false": False}[
                (
                    staff_pick
                    if staff_pick not in ["default", None]
                    else request.state.staff_pick
                )
            ],
            "min_rating": min_rating,
            "max_rating": max_rating,
            "status": level_status,
            "tags": [tag.strip() for tag in tags] if tags else [],
            "min_likes": min_likes,
            "max_likes": max_likes,
            "min_comments": min_comments,
            "max_comments": max_comments,
            "liked_by": liked_by,
            "commented_on": commented_on,
            "title_includes": title_includes,
            "description_includes": description_includes,
            "author_includes": author_includes,
            "artists_includes": artists_includes,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "meta_includes": keywords,
        }
    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.get(
            request.app.api_config["url"] + "/api/charts/",
            params={
                k: (int(v) if isinstance(v, bool) else v)
                for k, v in params.items()
                if v is not None
            },
        ) as req:
            response = LevelList.model_validate(await req.json()) # await req.json()
    pageCount = response.pageCount
    if sort_by == "random" and pageCount != 0 and len(response.data) == 10:
        pageCount = (
            page + 2
        )  # always have one extra page, random will not run out and there may be duplicates
        # only if pageCount isn't 0 of course, and the api actually returned a full list (so there likely is more)
    if page > pageCount or page < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                locale.invalid_page_plural(page, pageCount)
                if pageCount != 1
                else locale.invalid_page_singular(page, pageCount)
            ),
        )
    elif pageCount == 0:
        raise HTTPException(
            status_code=400, detail=locale.items_not_found_search("level")
        )
    asset_base_url = response.asset_base_url.removesuffix("/")
    data = await asyncio.gather(
        *[
            request.app.run_blocking(
                item.to_level_item,
                request,
                asset_base_url,
                request.state.levelbg,
            )
            for item in response.data
        ]
    )
    num_pages = pageCount
    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                locale.items_not_found("level")
                if not searching
                else locale.items_not_found_search("level")
            ),
        )
    page_data = handle_item_uwu(data, request.state.localization, uwu_level)
    return {
        "pageCount": num_pages,
        "items": page_data,
    }
