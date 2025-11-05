import asyncio

from typing import List

from fastapi import APIRouter, Request
from core import SonolusRequest
from helpers.models.sonolus.item_section import LevelItemSection
from helpers.models.sonolus.response import ServerItemInfo
from helpers.models.sonolus.options import ServerForm
from helpers.models.api.levels import LevelList

from helpers.api_helpers import api_level_to_level
from helpers.data_helpers import (
    create_section,
    create_server_form,
    ServerFormOptionsFactory,
)
from helpers.data_compilers import compile_banner

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_uwu, handle_item_uwu

import aiohttp


@router.get("/")
async def main(request: SonolusRequest):
    locale = request.state.loc
    uwu_level = request.state.uwu
    banner_srl = await request.app.run_blocking(compile_banner)
    searches = []
    creates = []
    auth = request.headers.get("Sonolus-Session")

    # TODO TODO: continue

    creates = [
        ServerForm(
            type="level",
            title="#UPLOAD",
            icon="level",
            requireConfirmation=True,
            options=[],
            description=locale.use_website_to_upload("https://untitledcharts.com")
        )
    ]
    staff_pick = request.state.staff_pick
    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    async with aiohttp.ClientSession(headers=headers) as cs:
        url = request.app.api_config["url"] + "/api/charts/"
        staff_pick_value = {"off": None, "true": 1, "false": 0}[staff_pick]
        random_params = {"type": "random"}
        if staff_pick_value:
            random_params["staff_pick"] = staff_pick_value
        newest_params = {"type": "advanced", "sort_by": "published_at"}
        if staff_pick_value:
            newest_params["staff_pick"] = staff_pick_value
        popular_params = {
            "type": "advanced",
            "sort_by": "decaying_likes",
        }
        if staff_pick_value:
            popular_params["staff_pick"] = staff_pick_value
        tasks = [
            cs.get( # TODO: more convenient uhh
                url,
                params=random_params,
            ),
            cs.get(
                url,
                params=newest_params,
            ),
            cs.get(
                url,
                params={
                    "type": "random",
                    "staff_pick": {"true": 1, "false": 0}[
                        ("true" if staff_pick in ["off", "false"] else "false")
                    ],
                },
            ),
            cs.get(
                url,
                params=popular_params,
            ),
        ]
        responses = await asyncio.gather(*tasks)

        random_response = LevelList.model_validate(await responses[0].json())
        newest_response = LevelList.model_validate(await responses[1].json())
        staffpick_req = LevelList.model_validate(await responses[2].json())
        popular_response = LevelList.model_validate(await responses[3].json())

        # random_response, newest_response, staffpick_req, popular_response = ( TODO
        #     await asyncio.gather(*[resp.json() for resp in responses])
        # )
    asset_base_url = random_response.asset_base_url.removesuffix("/")
    random_staff_pick = await request.app.run_blocking(
        staffpick_req.data[0].to_level,
        request,
        asset_base_url,
        request.state.levelbg
    )
    random = await asyncio.gather(
        *[
            request.app.run_blocking(
                api_level_to_level,
                request,
                asset_base_url,
                i,
                request.state.levelbg,
            )
            for i in random_response["data"][:3]
        ]
    )
    newest = await asyncio.gather(
        *[
            request.app.run_blocking(
                api_level_to_level,
                request,
                asset_base_url,
                i,
                request.state.levelbg,
            )
            for i in newest_response["data"][:3]
        ]
    )
    popular = await asyncio.gather(
        *[
            request.app.run_blocking(
                api_level_to_level,
                request,
                asset_base_url,
                i,
                request.state.levelbg,
            )
            for i in popular_response["data"][:3]
        ]
    )
    sections: List[LevelItemSection] = [
        create_section(
            (
                locale.random_staff_pick
                if staff_pick in ["off", "false"]
                else locale.random_non_staff_pick
            ),
            item_type,
            handle_item_uwu(
                [random_staff_pick], request.state.localization, uwu_level
            ),
            icon="trophy",
            description=handle_uwu(
                (
                    locale.staff_pick_desc
                    if staff_pick in ["off", "false"]
                    else locale.non_staff_pick_desc
                ),
                request.state.localization,
                uwu_level,
            ),
        ),
        create_section(
            "#NEWEST",
            item_type,
            handle_item_uwu(newest, request.state.localization, uwu_level),
            icon="level",
        ),
        create_section(
            "#RANDOM",
            item_type,
            handle_item_uwu(random, request.state.localization, uwu_level),
            icon="level",
        ),
        create_section(
            "#POPULAR",
            item_type,
            handle_item_uwu(popular, request.state.localization, uwu_level),
            icon="level",
        ),
    ]
    options = []
    options.append(
        ServerFormOptionsFactory.server_text_option(
            query="keywords",
            name="#KEYWORDS",
            required=False,
            default="",
            placeholder=locale.search.ENTER_TEXT,
            limit=100,
            shortcuts=[],
        )
    )
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="staff_pick",
            name=locale.staff_pick,
            required=False,
            default="default",
            description=handle_uwu(
                locale.search.STAFF_PICK_DESC, request.state.localization, uwu_level
            ),
            values=[
                {"name": "default", "title": "#DEFAULT"},
                {"name": "off", "title": locale.search.STAFF_PICK_OFF},
                {"name": "true", "title": locale.search.STAFF_PICK_TRUE},
                {"name": "false", "title": locale.search.STAFF_PICK_FALSE},
            ],
        )
    )
    options.append(
        ServerFormOptionsFactory.server_slider_option(
            query="min_rating",
            name=locale.search.MIN_RATING,
            required=False,
            default=-999,
            min_value=-999,
            max_value=999,
            step=1,
        )
    )
    options.append(
        ServerFormOptionsFactory.server_slider_option(
            query="max_rating",
            name=locale.search.MAX_RATING,
            required=False,
            default=999,
            min_value=-999,
            max_value=999,
            step=1,
        )
    )
    options.append(
        ServerFormOptionsFactory.server_text_option(
            query="title_includes",
            name=locale.search.TITLE_CONTAINS,
            required=False,
            default="",
            placeholder=locale.search.ENTER_TEXT,
            limit=100,
            shortcuts=[],
        )
    )
    options.append(
        ServerFormOptionsFactory.server_text_option(
            query="author_includes",
            name=locale.search.AUTHOR_CONTAINS,
            required=False,
            default="",
            placeholder=locale.search.ENTER_TEXT,
            limit=60,
            shortcuts=[],
        )
    )
    options.append(
        ServerFormOptionsFactory.server_text_option(
            query="description_includes",
            name=locale.search.DESCRIPTION_CONTAINS,
            required=False,
            default="",
            placeholder=locale.search.ENTER_TEXT,
            limit=200,
            shortcuts=[],
        )
    )
    options.append(
        ServerFormOptionsFactory.server_text_option(
            query="artists_includes",
            name=locale.search.ARTISTS_CONTAINS,
            required=False,
            default="",
            placeholder=locale.search.ENTER_TEXT,
            limit=100,
            shortcuts=[],
        )
    )
    if auth:
        options.append(
            ServerFormOptionsFactory.server_toggle_option(
                query="liked_by",
                name=locale.search.ONLY_LEVELS_I_LIKED,
                required=False,
                default=False,
            )
        )
        options.append(
            ServerFormOptionsFactory.server_toggle_option(
                query="commented_on",
                name=locale.search.ONLY_LEVELS_I_COMMENTED_ON,
                required=False,
                default=False,
            )
        )

    options.append(
        ServerFormOptionsFactory.server_slider_option(
            query="min_likes",
            name=locale.search.MIN_LIKES,
            required=False,
            default=0,
            min_value=0,
            max_value=9999,
            step=1,
        )
    )
    options.append(
        ServerFormOptionsFactory.server_slider_option(
            query="max_likes",
            name=locale.search.MAX_LIKES,
            required=False,
            default=9999,
            min_value=0,
            max_value=9999,
            step=1,
        )
    )
    options.append(
        ServerFormOptionsFactory.server_slider_option(
            query="min_comments",
            name=locale.search.MIN_COMMENTS,
            required=False,
            default=0,
            min_value=0,
            max_value=9999,
            step=1,
        )
    )
    options.append(
        ServerFormOptionsFactory.server_slider_option(
            query="max_comments",
            name=locale.search.MAX_COMMENTS,
            required=False,
            default=9999,
            min_value=0,
            max_value=9999,
            step=1,
        )
    )
    options.append(
        ServerFormOptionsFactory.server_text_option(
            query="tags",
            name=locale.search.TAGS_COMMA_SEPARATED,
            required=False,
            default="",
            placeholder=locale.search.ENTER_TAGS,
            limit=200,
            shortcuts=[],
        )
    )
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="sort_by",
            name=locale.search.SORT_BY,
            required=False,
            default="published_at",
            values=[
                {"name": "published_at", "title": locale.search.DATE_PUBLISHED},
                {"name": "created_at", "title": locale.search.DATE_CREATED},
                {"name": "random", "title": "#RANDOM"},
                {"name": "rating", "title": locale.search.RATING},
                {"name": "likes", "title": locale.search.LIKES},
                {"name": "comments", "title": locale.search.COMMENTS},
                {
                    "name": "decaying_likes",
                    "title": locale.search.DECAYING_LIKES,
                },
                {"name": "abc", "title": locale.search.TITLE_A_Z},
            ],
            description=handle_uwu(
                locale.search.SORT_BY_DESCRIPTION,
                request.state.localization,
                uwu_level,
            ),
        )
    )
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="sort_order",
            name=locale.search.SORT_ORDER,
            required=False,
            default="desc",
            values=[
                {"name": "desc", "title": locale.search.DESCENDING},
                {"name": "asc", "title": locale.search.ASCENDING},
            ],
        )
    )
    search_form = create_server_form(
        type="advanced",
        title=locale.search.ADVANCED_SEARCH,
        require_confirmation=False,
        options=options,
    )
    searches.append(search_form)

    data: ServerItemInfo = {
        "sections": sections,
    }
    if banner_srl:
        data["banner"] = banner_srl
    if searches:
        data["searches"] = searches
    if creates:
        data["creates"] = creates
    return data
