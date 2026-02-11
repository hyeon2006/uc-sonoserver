import base64, asyncio

from fastapi import APIRouter
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.data_compilers import compile_playlists_list
from helpers.models.sonolus.options import (
    ServerForm,
    ServerOption_Value,
    ServerSelectOption,
    ServerSliderOption,
    ServerTextOption,
    ServerToggleOption,
)
from helpers.models.sonolus.submit import ServerSubmitPlaylistActionRequest
from helpers.models.sonolus.response import ServerItemDetails

router = APIRouter()

from helpers.owoify import handle_item_uwu, handle_uwu


@router.get("/", response_model=ServerItemDetails)
async def main(request: SonolusRequest, item_name: str):
    locale = request.state.loc
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")
    actions = []

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=locale.not_logged_in
        )
    if item_name == "uploaded":
        item_name = "uploaded_cGFnZT0x"  # page=1
    parts = item_name.split("_", 1)
    if parts[0] != "uploaded" or len(parts) != 2 or len(item_name) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="huh")
    params = ServerSubmitPlaylistActionRequest(values=parts[1]).parse(request)

    page = params.page or 1

    response = await request.app.api.charts_advanced_search(
        page=page - 1,
        staff_pick=params.staff_pick,
        min_rating=params.min_rating,
        max_rating=params.max_rating,
        status=params.level_status or "ALL",
        tags=params.tags,
        min_likes=params.min_likes,
        max_likes=params.max_likes,
        min_comments=params.min_comments,
        max_comments=params.max_comments,
        liked_by=params.liked_by,
        commented_on=params.commented_on,
        title_includes=params.title_includes,
        description_includes=params.description_includes,
        author_includes=params.author_includes,
        artists_includes=params.artists_includes,
        sort_by=params.sort_by,
        sort_order=params.sort_order,
        meta_includes=params.keywords,
    ).send(auth)

    asset_base_url = response.data.asset_base_url.removesuffix("/")
    levels = await asyncio.gather(
        *[
            request.app.run_blocking(
                chart.to_level_item,
                request,
                asset_base_url,
                request.state.levelbg,
            )
            for chart in response.data.data
        ]
    )
    pageCount = response.data.pageCount
    if params.sort_by == "random" and pageCount != 0 and len(response.data.data) == 10:
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
            status_code=400, detail=locale.items_not_found_search("uploaded")
        )
    item_data = (
        await request.app.run_blocking(
            compile_playlists_list,
            request.app.base_url,
            request.state.localization,
        )
    )[0].model_copy()
    item_data.name = item_name
    item_data.levels = levels
    options = [
        ServerSelectOption(
            query="level_status",
            name=locale.search.VISIBILITY,
            required=False,
            default=params.level_status or "ALL",
            values=[
                ServerOption_Value(name="ALL", title=locale.search.VISIBILITY_ALL),
                ServerOption_Value(
                    name="PUBLIC_MINE", title=locale.search.VISIBILITY_PUBLIC
                ),
                ServerOption_Value(
                    name="UNLISTED", title=locale.search.VISIBILITY_UNLISTED
                ),
                ServerOption_Value(
                    name="PRIVATE", title=locale.search.VISIBILITY_PRIVATE
                ),
            ],
        ),
        ServerSelectOption(
            query="staff_pick",
            name=locale.staff_pick,
            description=handle_uwu(
                locale.search.STAFF_PICK_DESC, request.state.localization, uwu_level
            ),
            required=False,
            default=(
                {None: "off", True: "true", False: "false"}[params.staff_pick]
                if not params.is_default_staff_pick
                else "default"
            ),
            values=[
                ServerOption_Value(name="default", title="#DEFAULT"),
                ServerOption_Value(name="off", title=locale.search.STAFF_PICK_OFF),
                ServerOption_Value(name="true", title=locale.search.STAFF_PICK_TRUE),
                ServerOption_Value(name="false", title=locale.search.STAFF_PICK_FALSE),
            ],
        ),
        ServerTextOption(
            query="keywords",
            name="#KEYWORDS",
            required=False,
            default=params.keywords or "",
            placeholder=locale.search.ENTER_TEXT,
            limit=100,
            shortcuts=[],
        ),
        ServerSliderOption(
            query="min_rating",
            name=locale.search.MIN_RATING,
            required=False,
            default=params.min_rating or -999,
            min=-999,
            max=999,
            step=1,
        ),
        ServerSliderOption(
            query="max_rating",
            name=locale.search.MAX_RATING,
            required=False,
            default=params.max_rating or 999,
            min=-999,
            max=999,
            step=1,
        ),
        ServerTextOption(
            query="title_includes",
            name=locale.search.TITLE_CONTAINS,
            required=False,
            default=params.title_includes or "",
            placeholder=locale.search.ENTER_TEXT,
            limit=100,
            shortcuts=[],
        ),
        ServerTextOption(
            query="author_includes",
            name=locale.search.AUTHOR_CONTAINS,
            required=False,
            default=params.author_includes or "",
            placeholder=locale.search.ENTER_TEXT,
            limit=60,
            shortcuts=[],
        ),
        ServerTextOption(
            query="description_includes",
            name=locale.search.DESCRIPTION_CONTAINS,
            required=False,
            default=params.description_includes or "",
            placeholder=locale.search.ENTER_TEXT,
            limit=200,
            shortcuts=[],
        ),
        ServerTextOption(
            query="artists_includes",
            name=locale.search.ARTISTS_CONTAINS,
            required=False,
            default=params.artists_includes or "",
            placeholder=locale.search.ENTER_TEXT,
            limit=100,
            shortcuts=[],
        ),
    ]

    options.append(
        ServerToggleOption(
            query="liked_by",
            name=locale.search.ONLY_LEVELS_I_LIKED,
            required=False,
            default=params.liked_by if params.liked_by is not None else False,
        )
    )

    options.append(
        ServerToggleOption(
            query="commented_on",
            name=locale.search.ONLY_LEVELS_I_COMMENTED_ON,
            required=False,
            default=params.commented_on if params.commented_on is not None else False,
        )
    )

    options.append(
        ServerSliderOption(
            query="min_likes",
            name=locale.search.MIN_LIKES,
            required=False,
            default=params.min_likes or 0,
            min=0,
            max=9999,
            step=1,
        )
    )
    options.append(
        ServerSliderOption(
            query="max_likes",
            name=locale.search.MAX_LIKES,
            required=False,
            default=params.max_likes or 9999,
            min=0,
            max=9999,
            step=1,
        )
    )
    options.append(
        ServerSliderOption(
            query="min_comments",
            name=locale.search.MIN_COMMENTS,
            required=False,
            default=params.min_comments or 0,
            min=0,
            max=9999,
            step=1,
        )
    )
    options.append(
        ServerSliderOption(
            query="max_comments",
            name=locale.search.MAX_COMMENTS,
            required=False,
            default=params.max_comments or 9999,
            min=0,
            max=9999,
            step=1,
        )
    )
    options.append(
        ServerTextOption(
            query="tags",
            name=locale.search.TAGS_COMMA_SEPARATED,
            required=False,
            default=", ".join(params.tags) if params.tags else "",
            placeholder=locale.search.ENTER_TAGS,
            limit=200,
            shortcuts=[],
        )
    )
    options.append(
        ServerSelectOption(
            query="sort_by",
            name=locale.search.SORT_BY,
            description=handle_uwu(
                locale.search.SORT_BY_DESCRIPTION,
                request.state.localization,
                uwu_level,
            ),
            required=False,
            default=params.sort_by or "created_at",
            values=[
                ServerOption_Value(name="created_at", title=locale.search.DATE_CREATED),
                ServerOption_Value(name="random", title="#RANDOM"),
                ServerOption_Value(name="rating", title=locale.search.RATING),
                ServerOption_Value(name="likes", title=locale.search.LIKES),
                ServerOption_Value(name="comments", title=locale.search.COMMENTS),
                ServerOption_Value(
                    name="decaying_likes", title=locale.search.DECAYING_LIKES
                ),
                ServerOption_Value(name="abc", title=locale.search.TITLE_A_Z),
            ],
        )
    )
    options.append(
        ServerSelectOption(
            query="sort_order",
            name=locale.search.SORT_ORDER,
            required=False,
            default=params.sort_order or "desc",
            values=[
                ServerOption_Value(name="desc", title=locale.search.DESCENDING),
                ServerOption_Value(name="asc", title=locale.search.ASCENDING),
            ],
        )
    )
    actions.append(
        ServerForm(
            type="filter",
            title=locale.search.FILTERS(page, pageCount),
            requireConfirmation=False,
            options=[
                ServerSliderOption(
                    query="page",
                    name="Page",
                    default=page,
                    min=1,
                    max=pageCount,
                    step=1,
                    required=False,
                )
            ]
            + options,
        )
    )

    return ServerItemDetails(
        item=handle_item_uwu([item_data], request.state.localization, uwu_level)[0],
        actions=actions,
        hasCommunity=False,
        leaderboards=[],
        sections=[],
    )
