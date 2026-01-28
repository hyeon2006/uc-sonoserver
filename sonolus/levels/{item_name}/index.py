from fastapi import APIRouter

from core import SonolusRequest
from helpers.models.sonolus.response import ServerItemDetails
from helpers.models.sonolus.options import ServerForm, ServerOption_Value, ServerSelectOption, ServerTextOption, ServerToggleOption
from helpers.models.sonolus.item import LevelItem, ServerItemLeaderboard

router = APIRouter()

from helpers.owoify import handle_item_uwu, handle_uwu


@router.get("/", response_model=ServerItemDetails)
async def main(request: SonolusRequest, item_name: str):
    locale = request.state.loc
    item_data: LevelItem = None
    auth = request.headers.get("Sonolus-Session")
    actions = []
    
    response = await request.app.api.get_chart(item_name).send(auth)

    asset_base_url = response.data.asset_base_url.removesuffix("/")
    liked = response.data.data.liked
    like_count = response.data.data.like_count
    item_data, desc = await request.app.run_blocking(
        response.data.data.to_level_item,
        request,
        asset_base_url,
        request.state.levelbg,
        include_description=True,
        context="level",
    )

    if auth:
        if liked:
            actions.append(
                ServerForm(
                    type="unlike",
                    title=f"Unlike ({like_count:,})", # TODO localize
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
    if response.data.mod or response.data.owner:
        if response.data.owner or response.data.admin:
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
        current = response.data.data.status
        visibility_values = []
        for s, meta in VISIBILITIES.items():
            visibility_values.append(ServerOption_Value(name=s, title=meta["title"]))

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
        if response.data.mod:
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
                            placeholder=str(response.data.data.rating),
                            description=locale.rerate_desc,
                            shortcuts=[str(response.data.data.rating)],
                            limit=9 # -999.1234, 9 max possible characters
                        )
                    ]
                )
            )
            if response.data.data.staff_pick:
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

    data: LevelItem = handle_item_uwu([item_data], request.state.localization, request.state.uwu)[0]

    return ServerItemDetails(
        item=data,
        description=desc,
        actions=actions,
        hasCommunity=True,
        leaderboards=[ # TODO: localize
            ServerItemLeaderboard(
                name="arcade_score_speed",
                title=handle_uwu("Arcade Score", request.state.localization)
            ),
            ServerItemLeaderboard(
                name="accuracy_score",
                title="Accuracy Score"
            ),
            ServerItemLeaderboard(
                name="arcade_score_no_speed",
                title="Arcade Score w/o speed bonus"
            ),
            ServerItemLeaderboard(
                name="rank_match",
                title="Rank Match"
            ),
            ServerItemLeaderboard(
                name="least_combo_breaks",
                title="Least combo breaks"
            ),
            ServerItemLeaderboard(
                name="least_misses",
                title="Least misses"
            ),
            ServerItemLeaderboard(
                name="perfect",
                title="Perfect count"
            )
        ],
        sections=[]
    )
