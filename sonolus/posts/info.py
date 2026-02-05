from typing import Literal
from fastapi import APIRouter
from core import SonolusRequest
from helpers.models.sonolus.item_section import PostItemSection
from helpers.models.sonolus.options import ServerForm, ServerSelectOption, ServerOption_Value
from helpers.models.sonolus.response import ServerItemInfo
from helpers.data_compilers import (
    compile_banner,
    compile_static_posts_list,
    sort_posts_by_newest
)

router = APIRouter()

from helpers.owoify import handle_item_uwu


@router.get("/", response_model=ServerItemInfo)
async def main(request: SonolusRequest, type: Literal["announcements", "notifications"]):
    uwu_level = request.state.uwu
    banner_srl = await request.app.run_blocking(compile_banner)
    locale = request.state.loc

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
                    items=[
                        post.to_post_item()
                        for post in
                        handle_item_uwu(data[:5], request.state.localization, uwu_level)
                    ]
                ),
            ]
        case "notifications":
            auth = request.headers.get("Sonolus-Session")

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
    
    return ServerItemInfo(
        sections=sections,
        searches=[
            ServerForm(
                type="advanced",
                title="#ADVANCED",
                icon="advanced",
                requireConfirmation=False,
                options=[
                    ServerSelectOption(
                        query="post_type",
                        name="#TYPE",
                        required=False,
                        default="all",
                        values=[
                            ServerOption_Value(name="all", title="#ALL"),
                            ServerOption_Value(name="announcements", title=request.state.loc.announcements),
                            ServerOption_Value(name="notifications", title=request.state.loc.notification.NOTIFICATION)
                        ]
                    )
                ]
            )
        ],
        banner=banner_srl if banner_srl else None
    )
