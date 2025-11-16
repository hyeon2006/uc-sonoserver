from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.models.sonolus.response import ServerItemDetails
from helpers.models.sonolus.options import ServerForm, ServerSelectOption, ServerTextOption, ServerToggleOption
from helpers.models.api.levels import GetChartResponse
from helpers.models.sonolus.item import LevelItem
from helpers.data_helpers import create_server_form, ServerFormOptionsFactory
from helpers.api_helpers import api_level_to_level_item

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_item_uwu

import aiohttp


@router.get("/", response_model=ServerItemDetails)
async def main(request: SonolusRequest, item_name: str):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    uwu_handled = False
    item_data: LevelItem = None
    auth = request.headers.get("Sonolus-Session")
    actions = []
    
    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.get(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/"
        ) as req:
            data = await req.json()
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=response["detail"]
                )
            response = GetChartResponse.model_validate_json(await req.json())

    asset_base_url = response.asset_base_url.removesuffix("/")
    liked = response.data.liked
    like_count = response.data.like_count
    item_data, desc = await request.app.run_blocking(
        api_level_to_level_item,
        request,
        asset_base_url,
        response.data,
        request.state.levelbg,
        include_description=True,
        context="level",
    )
    if auth:
        if liked:
            actions.append(
                ServerForm(
                    type="unlike",
                    title=f"Unlike ({like_count:,})", # XXX shouldn't it be localised?
                    icon="heart",
                    requireConfirmation=False,
                    options=[]
                ),
            )
        else:
            actions.append(
                ServerForm(
                    type="like",
                    title=f"Like ({like_count:,})",
                    icon="heartHollow",
                    requireConfirmation=False,
                    options=[]
                ),
            )
    if response.mod or response.owner:
        if response.owner or response.admin:
            actions.append(
                ServerForm(
                    type="delete",
                    title="#DELETE",
                    icon="delete",
                    requireConfirmation=True,
                    options=[]
                )
            )
        VISIBILITIES = {
            "PUBLIC": {"title": "#PUBLIC", "icon": "globe"},
            "PRIVATE": {"title": "#PRIVATE", "icon": "lock"},
            "UNLISTED": {
                "title": locale.search.VISIBILITY_UNLISTED,
                "icon": "unlock", # XXX maybe "hide" would be better
            },
        }
        current = response["data"]["status"]
        visibility_values = []
        for s, meta in VISIBILITIES.items():
            visibility_values.append({"name": s, "title": meta["title"]})

        actions.append(ServerForm(
            type="visibility",
            title=locale.search.VISIBILITY,
            icon=VISIBILITIES[current]["icon"],
            requireConfirmation=True,
            options=[
                ServerSelectOption(
                    query="visibility",
                    name=locale.search.VISIBILITY,
                    required=True,
                    default=current,
                    values=visibility_values
                )
            ]
        ))
        if response.mod:
            actions.append(
                ServerForm(
                    type="rerate",
                    title=locale.rerate,
                    icon="plus",
                    requireConfirmation=True,
                    options=[
                        ServerTextOption(
                            query="constant",
                            name="#RATING",
                            required=True,
                            default="",
                            placeholder=str(response.data.rating),
                            description=locale.rerate_desc,
                            shortcuts=[str(response.data.rating)],
                            limit=9 # -999.1234, 9 max possible characters
                        )
                    ]
                )
            )
            if response.data.staff_pick:
                actions.append(
                    ServerForm(
                        type="staff_pick_delete",
                        title=locale.staff_pick_remove,
                        icon="delete",
                        requireConfirmation=True,
                        options=[
                            ServerToggleOption(
                                query="_",
                                name="#CONFIRM",
                                description=locale.staff_pick_confirm, # no uwu
                                required=True,
                                default=False
                            )
                        ]
                    )
                )
            else:
                actions.append(
                    ServerForm(
                        type="staff_pick_add",
                        title=locale.staff_pick_add,
                        icon="trophy",
                        requireConfirmation=True,
                        options=[
                            ServerToggleOption(
                                query="_",
                                name="#CONFIRM",
                                required=True,
                                default=False,
                                description=locale.staff_pick_confirm
                            )
                        ]
                    )
                )
        uwu_handled = True

    if uwu_handled:
        data = item_data
    else:
        data: LevelItem = handle_item_uwu([item_data], request.state.localization, uwu_level)[0]

    return ServerItemDetails(
        item=data,
        description=desc,
        actions=actions,
        hasCommunity=True,
        leaderboards=[], # TODO
        sections=[]
    )
