from fastapi import APIRouter
from core import SonolusRequest
from helpers.models.sonolus.item_section import PostItemSection
from helpers.models.sonolus.response import ServerItemInfo
from helpers.data_compilers import (
    compile_banner,
    compile_static_posts_list,
    sort_posts_by_newest
)

router = APIRouter()

from helpers.owoify import handle_item_uwu


@router.get("/")
async def main(request: SonolusRequest):
    locale = request.state.loc
    uwu_level = request.state.uwu
    banner_srl = await request.app.run_blocking(compile_banner)
    searches = []
    creates = []
    auth = request.headers.get("Sonolus-Session")

    data = await request.app.run_blocking(
        compile_static_posts_list, request.app.base_url
    )
    data = sort_posts_by_newest(data)
    sections = [
        PostItemSection(
            title="#NEWEST",
            icon="post",
            items=handle_item_uwu(data[:5], request.state.localization, uwu_level)
        ),
    ]
    if auth:
        response = await request.app.api.get_notifications(only_unread=True).send(auth)

        notifs = response.data.to_posts(request)
        if notifs:
            sections.insert(
                0,
                PostItemSection(
                    title=locale.notification.UNREAD,
                    icon="bell",
                    description=locale.notification.NOTIFICATION_DESC_UNREAD,
                    items=notifs
                )
            )
        else:
            sections.insert(
                0,
                PostItemSection(
                    title=locale.notification.NOTIFICATION,
                    icon="bell",
                    description=locale.notification.NOTIFICATION_DESC,
                    items=[]
                )
            )
    
    return ServerItemInfo(
        creates=creates if creates else None,
        searches=searches if searches else None,
        sections=sections,
        banner=banner_srl if banner_srl else None
    )
