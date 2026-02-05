from fastapi import APIRouter, HTTPException, status

from core import SonolusRequest
from helpers.models.sonolus.item import UserItem
from helpers.models.sonolus.item_section import LevelItemSection
from helpers.models.sonolus.misc import Tag
from helpers.models.sonolus.response import ServerItemDetails
from helpers.owoify import handle_item_uwu

router = APIRouter()


@router.get("/", response_model=ServerItemDetails)
async def main(request: SonolusRequest, user_id: str):
    profile = await request.app.api.get_user_profile(user_id).send()

    tags = []

    if profile.status == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if profile.data.account.admin:
        tags.append(Tag(title="#ADMIN", icon="crown"))
    elif profile.data.account.mod:
        tags.append(Tag(title="#MODERATOR", icon="crown"))

    if profile.data.account.banned:
        tags.append(Tag(title="#BANNED", icon="lock"))

    return ServerItemDetails(
        item=UserItem(
            name=profile.data.account.sonolus_id,
            title=profile.data.account.sonolus_username,
            handle=str(profile.data.account.sonolus_handle),
            tags=tags
        ),
        actions=[],
        hasCommunity=False,
        leaderboards=[],
        sections=[
            LevelItemSection(
                title="#NEWEST",
                icon="level",
                items=handle_item_uwu(
                    [
                        await request.app.run_blocking(
                            chart.to_level_item,
                            request,
                            profile.data.asset_base_url,
                            request.state.levelbg
                        )
                        for chart in profile.data.charts
                    ],
                    request.state.localization,
                    request.state.uwu
                )
            )
        ]
    )