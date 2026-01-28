from fastapi import APIRouter

from core import SonolusRequest
from helpers.data_compilers import compile_banner
from helpers.models.sonolus.item_section import ReplayItemSection
from helpers.models.sonolus.options import ServerForm, ServerToggleOption
from helpers.models.sonolus.response import ServerItemInfo
from helpers.owoify import handle_item_uwu

router = APIRouter()

@router.get("/")
async def info(request: SonolusRequest):
    random = await request.app.api.get_random_leaderboard_records(limit=3).send()
    newest = await request.app.api.get_recent_leaderboard_records().send()

    return ServerItemInfo(
        searches=[
            ServerForm(
                type="advanced",
                title="#ADVANCED",
                requireConfirmation=False,
                options=[
                    ServerToggleOption(
                        query="random",
                        name="#RANDOM",
                        default=False
                    )
                ]
            )
        ],
        sections=[
            ReplayItemSection(
                title="#RANDOM",
                icon="replay",
                items=handle_item_uwu(
                    await request.app.run_blocking(
                        random.data.to_replay_items,
                        request
                    ),
                    request.state.localization
                ),
            ),
            ReplayItemSection(
                title="#NEWEST",
                icon="replay",
                items=handle_item_uwu(
                    await request.app.run_blocking(
                        newest.data.to_replay_items,
                        request
                    ),
                    request.state.localization,
                    request.state.uwu
                )
            )
        ],
        banner=await request.app.run_blocking(compile_banner)
    )