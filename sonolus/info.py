import aiohttp

from fastapi import APIRouter, Request, HTTPException, status

from helpers.data_compilers import (
    compile_banner,
    compile_particles_list,
    compile_engines_list,
    compile_skins_list,
)
from helpers.datastructs import ServerInfoButton
from helpers.data_helpers import (
    ServerFormOptionsFactory,
)

from typing import List

from locales.locale import Loc
from helpers.owoify import handle_uwu

router = APIRouter()


@router.get("/")
async def main(request: Request):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    # Assume logged in
    # We only need to validate the session
    # If it's a request that updates something, or access something private
    logged_in = False
    if request.headers.get("Sonolus-Session"):
        logged_in = True

    uwu_supported = ["en", "tr"]

    banner_srl = await request.app.run_blocking(compile_banner)
    button_list = ["authentication", "post", "level", "configuration"]
    if logged_in:
        button_list.append("playlist")
    if request.state.showresourcebuttons:
        button_list.extend(
            [
                "skin",
                "background",
                "effect",
                "particle",
                "engine",
            ]
        )
    options = []
    if request.state.localization in uwu_supported:
        option = ServerFormOptionsFactory.server_select_option(
            query="uwu",
            name=locale.uwu,
            required=False,
            default="off",
            values=[
                {"name": "off", "title": locale.off},
                {"name": "owo", "title": locale.slightly},
                {"name": "uwu", "title": locale.a_lot},
                {"name": "uvu", "title": locale.extreme},
            ],
            description=handle_uwu(
                locale.uwu_desc, request.state.localization, request.state.uwu
            ),
        )
        options.append(option)
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="levelbg",
            name=locale.background.USEBACKGROUND,
            required=False,
            default="default_or_v3",
            values=[
                {"name": "default_or_v3", "title": locale.background.DEF_OR_V3},
                {"name": "v3", "title": locale.background.V3},
                {"name": "default_or_v1", "title": locale.background.DEF_OR_V1},
                {"name": "v1", "title": locale.background.V1},
            ],
            description=handle_uwu(
                locale.background.USEBACKGROUNDDESC,
                request.state.localization,
                uwu_level,
            ),
        )
    )
    engines = await request.app.run_blocking(
        compile_engines_list, request.app.base_url, request.state.localization
    )
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="defaultengine",
            name=locale.default_engine,
            required=False,
            default=engines[0]["name"],
            values=[{"name": item["name"], "title": item["title"]} for item in engines],
            description=handle_uwu(
                locale.default_engine_desc, request.state.localization, uwu_level
            ),
        )
    )
    skins = await request.app.run_blocking(compile_skins_list, request.app.base_url)
    unique_themes = []
    seen_themes = set()

    for item in skins:
        themes = item["themes"]
        for theme in themes:
            if theme not in seen_themes:
                unique_themes.append(theme)
                seen_themes.add(theme)
    unique_themes = sorted(unique_themes)
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="defaultskin",
            name=locale.default_skin,
            required=False,
            default="engine_default",
            values=[{"name": "engine_default", "title": "#DEFAULT"}]
            + [{"name": theme, "title": theme} for theme in unique_themes],
            description=handle_uwu(
                locale.default_skin_desc, request.state.localization, uwu_level
            ),
        )
    )
    particles = await request.app.run_blocking(
        compile_particles_list, request.app.base_url
    )
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="defaultparticle",
            name=locale.default_particle,
            required=False,
            default="engine_default",
            values=[{"name": "engine_default", "title": "#DEFAULT"}]
            + [
                {"name": item["name"], "title": item["title"]}
                for item in particles
                if item.get("engine_specific", False) == False
            ],
            description=handle_uwu(
                locale.default_particle_desc, request.state.localization, uwu_level
            ),
        )
    )
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="stpickconfig",
            name=locale.staff_pick,
            required=False,
            default="off",
            values=[
                {"name": "off", "title": locale.search.STAFF_PICK_OFF},
                {"name": "true", "title": locale.search.STAFF_PICK_TRUE},
                {"name": "false", "title": locale.search.STAFF_PICK_FALSE},
            ],
            description=handle_uwu(
                locale.search.STAFF_PICK_CONFIG_DESC + "\n" + locale.staff_pick_desc,
                request.state.localization,
                uwu_level,
            ),
        )
    )
    options.append(
        ServerFormOptionsFactory.server_toggle_option(
            query="showresourcebuttons",
            name=locale.show_resource_buttons,
            required=False,
            default="off",
            values=[
                {"name": "off", "title": locale.off},
                {"name": "on", "title": locale.on},
            ],
        )
    )
    desc = locale.server_description or request.app.config["description"]

    auth = request.headers.get("Sonolus-Session")
    login_message = False
    if auth:
        try:
            headers = {request.app.auth_header: request.app.auth}
            headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + f"/api/accounts/session/account/",
                ) as req:
                    response = await req.json()
            desc += "\n\n" + ("-" * 40) + "\n"
            desc += "\n" + locale.welcome(response["sonolus_username"])
            notifications = response["unread_notifications"]
            desc += "\n\n" + (
                locale.notifications_singular(notifications)
                if notifications == 1
                else (
                    locale.notifications_plural(notifications)
                    if notifications > 0
                    else locale.notification.none
                )
            )
            if notifications > 0:
                button_list = ["post"]
            desc += "\n\n" + ("-" * 40) + "\n"
            desc += f"\n{locale.find_in_playlists}"
            if response.get("mod") or response.get("admin"):
                desc += "\n\n" + ("-" * 40) + "\n"
                if response.get("admin"):
                    desc += f"\n{locale.is_admin}\n\n{locale.admin_powers}\n{locale.mod_powers}"
                else:
                    desc += f"\n{locale.is_mod}\n\n{locale.mod_powers}"
            login_message = True
        except:
            pass
    if not login_message:
        desc = locale.server_description or request.app.config["description"]
        desc += "\n\n" + ("-" * 40) + "\n"
        desc += "\n" + locale.not_logged_in
    buttons: List[ServerInfoButton] = [{"type": button} for button in button_list]
    data = {
        "title": request.app.config["name"],
        "description": handle_uwu(
            desc,
            request.state.localization,
            uwu_level,
        ),
        "buttons": buttons,
        "configuration": {"options": options},
    }
    if banner_srl:
        data["banner"] = banner_srl
    return data
