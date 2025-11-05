import asyncio

from fastapi import APIRouter, Request, Query
from fastapi import HTTPException, status

from typing import Literal, Optional, List

import aiohttp

from core import SonolusRequest
from helpers.paginate import list_to_pages
from helpers.sonolus_typings import ItemType
from helpers.api_helpers import api_level_to_level

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_item_uwu

type_func = type


@router.get("/")
async def main(
    request: SonolusRequest,
    item_type: ItemType,
    type: Literal["quick", "advanced"] = Query("quick"),
    page: int = Query(0, ge=0),
    staff_pick: Optional[Literal["default", "off", "true", "false"]] = Query("default"),
    min_rating: Optional[int] = Query(None),
    max_rating: Optional[int] = Query(None),
    tags: Optional[List[str]] = Query(None),
    min_likes: Optional[int] = Query(None),
    max_likes: Optional[int] = Query(None),
    min_comments: Optional[int] = Query(None),
    max_comments: Optional[int] = Query(None),
    liked_by: Optional[bool] = Query(False),
    commented_on: Optional[bool] = Query(False),
    title_includes: Optional[str] = Query(None),
    description_includes: Optional[str] = Query(None),
    author_includes: Optional[str] = Query(None),
    artists_includes: Optional[str] = Query(None),
    sort_by: Optional[
        Literal[
            "created_at",
            "published_at",
            "rating",
            "likes",
            "comments",
            "decaying_likes",
            "abc",
            "random",
        ]
    ] = Query("published_at"),
    sort_order: Optional[Literal["desc", "asc"]] = Query("desc"),
    level_status: Optional[Literal["PUBLIC"]] = Query(
        "PUBLIC"
    ),  # will only ever be PUBLIC here. anything else, go to playlists
    keywords: Optional[str] = Query(None),
):
    locale = request.state.loc
    uwu_level = request.state.uwu
    searching = False
    generate_pages = True
    auth = request.headers.get("Sonolus-Session")

    if item_type == "levels":
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
                "tags": tags,
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
                response = await req.json()
        pageCount = response["pageCount"]
        if sort_by == "random" and pageCount != 0 and len(response["data"]) == 10:
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
                status_code=400, detail=locale.items_not_found_search(item_type)
            )
        response_data = response["data"]
        asset_base_url = response["asset_base_url"].removesuffix("/")
        data = await asyncio.gather(
            *[
                request.app.run_blocking(
                    api_level_to_level,
                    request,
                    asset_base_url,
                    item,
                    request.state.levelbg,
                )
                for item in response_data
            ]
        )
        num_pages = pageCount
        generate_pages = False

    if generate_pages:
        pages = list_to_pages(data, request.app.get_items_per_page(item_type))
        if len(pages) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    locale.items_not_found(item_type)
                    if not searching
                    else locale.items_not_found_search(item_type)
                ),
            )
        try:
            page_data = pages[page]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="hi stop hitting our api thanks",
            )
    else:
        if len(data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    locale.items_not_found(item_type)
                    if not searching
                    else locale.items_not_found_search(item_type)
                ),
            )
        page_data = data
    page_data = handle_item_uwu(page_data, request.state.localization, uwu_level)
    return {
        "pageCount": len(pages) if generate_pages else num_pages,
        "items": page_data,
    }
