from typing import Literal
from fastapi import APIRouter, HTTPException, status
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
async def main(request: SonolusRequest, type: Literal["announcements", "notifications"] | str):
    locale = request.state.loc
    uwu_level = request.state.uwu
    banner_srl = await request.app.run_blocking(compile_banner) # TODO: check banners everywhere
    auth = request.headers.get("Sonolus-Session")

    match type:
        case "announcements":
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
        case "notifications":
            response = await request.app.api.get_notifications(only_unread=True).send(auth)

            notifs = response.data.to_posts(request)
            if notifs:
                sections = [
                    PostItemSection(
                        title=locale.notification.UNREAD,
                        icon="bell",
                        description=locale.notification.NOTIFICATION_DESC_UNREAD,
                        items=notifs
                    )
                ]
            else:
                sections = [
                    PostItemSection(
                        title=locale.notification.NOTIFICATION,
                        icon="bell",
                        description=locale.notification.NOTIFICATION_DESC,
                        items=[]
                    )
                ]
        case _:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=locale.item_type_not_found(type))
    
    return ServerItemInfo(
        sections=sections,
        banner=banner_srl if banner_srl else None
    )
