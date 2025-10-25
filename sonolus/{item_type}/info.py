import asyncio

from typing import List

from fastapi import APIRouter, Request
from fastapi import HTTPException, status
from helpers.sonolus_typings import ItemType
from helpers.datastructs import (
    EngineItemSection,
    SkinItemSection,
    BackgroundItemSection,
    EffectItemSection,
    ParticleItemSection,
    PostItemSection,
    PlaylistItemSection,
    LevelItemSection,
    ReplayItemSection,
    RoomItemSection,
    ServerItemInfo,
    ServerForm,
)
from helpers.api_helpers import api_level_to_level, api_notif_to_post
from helpers.data_helpers import (
    create_section,
    create_server_form,
    ServerFormOptionsFactory,
)
from helpers.data_compilers import (
    compile_banner,
    compile_backgrounds_list,
    compile_effects_list,
    compile_engines_list,
    compile_particles_list,
    compile_skins_list,
    compile_static_posts_list,
    sort_posts_by_newest,
    compile_playlists_list,
)

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_uwu, handle_item_uwu

import aiohttp


@router.get("/")
async def main(request: Request, item_type: ItemType):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    banner_srl = await request.app.run_blocking(compile_banner)
    searches = []
    creates = []
    auth = request.headers.get("Sonolus-Session")

    if item_type == "engines":
        data = await request.app.run_blocking(
            compile_engines_list, request.app.base_url, request.state.localization
        )
        sections: List[EngineItemSection] = [
            create_section(
                "#ENGINE",
                item_type,
                handle_item_uwu(data[:10], request.state.localization, uwu_level),
                description=handle_uwu(
                    locale.server_description or request.app.config["description"],
                    request.state.localization,
                    uwu_level,
                ),
                icon="engine",
            )
        ]
    elif item_type == "skins":
        data = await request.app.run_blocking(compile_skins_list, request.app.base_url)
        data = [
            item
            for item in data
            if (item.get("engines") == None)
            or (
                (type(item.get("engines")) in [list, tuple])
                and (request.state.engine in item.get("engines"))
            )
        ]
        sections: List[SkinItemSection] = [
            create_section(
                "#SKIN",
                item_type,
                handle_item_uwu(data[:10], request.state.localization, uwu_level),
                description=handle_uwu(
                    locale.server_description or request.app.config["description"],
                    request.state.localization,
                    uwu_level,
                ),
                icon="skin",
            )
        ]
    elif item_type == "backgrounds":
        data = await request.app.run_blocking(
            compile_backgrounds_list,
            request.app.base_url,
            request.state.localization,
        )
        sections: List[BackgroundItemSection] = [
            create_section(
                "#BACKGROUND",
                item_type,
                handle_item_uwu(data[:10], request.state.localization, uwu_level),
                description=handle_uwu(
                    locale.server_description or request.app.config["description"],
                    request.state.localization,
                    uwu_level,
                ),
                icon="background",
            )
        ]
    elif item_type == "effects":
        data = await request.app.run_blocking(
            compile_effects_list, request.app.base_url
        )
        sections: List[EffectItemSection] = [
            create_section(
                "#EFFECT",
                item_type,
                handle_item_uwu(data[:10], request.state.localization, uwu_level),
                description=handle_uwu(
                    locale.server_description or request.app.config["description"],
                    request.state.localization,
                    uwu_level,
                ),
                icon="effect",
            )
        ]
    elif item_type == "particles":
        data = await request.app.run_blocking(
            compile_particles_list, request.app.base_url
        )
        sections: List[ParticleItemSection] = [
            create_section(
                "#PARTICLE",
                item_type,
                handle_item_uwu(data[:10], request.state.localization, uwu_level),
                description=handle_uwu(
                    locale.server_description or request.app.config["description"],
                    request.state.localization,
                    uwu_level,
                ),
                icon="particle",
            )
        ]
    elif item_type == "posts":
        data = await request.app.run_blocking(
            compile_static_posts_list, request.app.base_url
        )
        data = sort_posts_by_newest(data)
        sections: List[PostItemSection] = [
            create_section(
                "#NEWEST",
                item_type,
                handle_item_uwu(data[:10], request.state.localization, uwu_level),
                icon="post",
            )
        ]
        if auth:
            headers = {request.app.auth_header: request.app.auth}
            headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + f"/api/accounts/notifications/",
                    params={"only_unread": 1},
                ) as req:
                    response = await req.json()
            raw_notifs = response.get("notifications", [])
            notifs = [api_notif_to_post(request, i) for i in raw_notifs]
            if notifs:
                sections.insert(
                    0,
                    create_section(
                        locale.notification.UNREAD,
                        item_type,
                        # don't uwuify. these are important
                        notifs,
                        icon="bell",
                        description=locale.notification.NOTIFICATION_DESC_UNREAD,
                    ),
                )
            else:
                sections.insert(
                    0,
                    create_section(
                        locale.notification.NOTIFICATION,
                        item_type,
                        [],
                        icon="bell",
                        description=locale.notification.NOTIFICATION_DESC,
                    ),
                )
    elif item_type == "playlists":
        data = await request.app.run_blocking(
            compile_playlists_list, request.app.base_url, request.state.localization
        )
        sections: List[PlaylistItemSection] = [
            create_section(
                "#PLAYLIST",
                item_type,
                data[:1],
                description=handle_uwu(
                    locale.server_description or request.app.config["description"],
                    request.state.localization,
                    uwu_level,
                ),
                icon="playlist",
            )
        ]
    elif item_type == "levels":
        creates = [
            create_server_form(
                type="level",
                title="#UPLOAD",
                icon="level",
                require_confirmation=True,
                options=[],
                description=locale.use_website_to_upload("https://untitledcharts.com"),
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
                cs.get(
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

            random_response, newest_response, staffpick_req, popular_response = (
                await asyncio.gather(*[resp.json() for resp in responses])
            )
        asset_base_url = random_response["asset_base_url"].removesuffix("/")
        random_staff_pick = await request.app.run_blocking(
            api_level_to_level,
            request,
            asset_base_url,
            staffpick_req["data"][0] if len(staffpick_req) > 0 else [],
            request.state.levelbg,
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
    # elif item_type == "replays":
    #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
    #     sections: List[ReplayItemSection] = [
    #         create_section(
    #             "Replays", item_type, data[:10], description=handle_uwu(
    #     locale.server_description or request.app.config["description"], request.state.localization,
    #     uwu_level,
    # ), icon="replay"
    #         )
    #     ]
    # elif item_type == "rooms":
    #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
    #     sections: List[RoomItemSection] = [
    #         create_section(
    #             "Rooms", item_type, data[:10], description=handle_uwu(
    #     locale.server_description or request.app.config["description"], request.state.localization,
    #     uwu_level,
    # ), icon="room"
    #         )
    #     ]
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=locale.item_type_not_found(item_type),
        )
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
