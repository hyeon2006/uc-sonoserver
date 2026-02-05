from datetime import datetime
from pydantic import BaseModel
from typing import TYPE_CHECKING
from helpers.models.sonolus.item import PostItem
from helpers.models.sonolus.misc import Tag

if TYPE_CHECKING:
    from core import SonolusRequest

class _BaseNotification(BaseModel):
    id: int
    title: str
    is_read: bool = False
    created_at: datetime = None
    timestamp: int # XXX (backend): remove timestamp?

    def to_post(self, request: "SonolusRequest") -> PostItem:
        loc = request.state.loc
        
        return PostItem(
            name=f"notification-{self.id}",
            source=request.app.base_url,
            title=self.title,
            time=self.timestamp,
            author="UntitledCharts",
            tags=[
                (
                    Tag(title=loc.notification.READ_STATUS, icon="envelopeOpen")
                    if self.is_read
                    else Tag(title=loc.notification.UNREAD_STATUS, icon="envelope")
                )
            ]
        )
    
class NotificationList(BaseModel):
    notifications: list[_BaseNotification]

    def to_posts(self, request) -> list[PostItem]:
        return [notification.to_post(request) for notification in self.notifications]

class Notification(_BaseNotification):
    user_id: str
    content: str


    def to_post(self, request: "SonolusRequest") -> tuple[PostItem, str]:
        post = super().to_post(request)
        loc = request.state.loc

        content_parts = self.content.splitlines()

        if content_parts[0].startswith("#"):
            match content_parts[0]:
                case "#CHART_DELETED":
                    del content_parts[0]
                    content = loc.notification.templates.CHART_DELETED(
                        chart_name="\n".join(content_parts)
                    )
                case "#CHART_VISIBILITY_CHANGED":
                    del content_parts[0]
                    content = loc.notification.templates.CHART_VISIBILITY_CHANGED(
                        visibility_status=content_parts.pop(0), chart_name="\n".join(content_parts)
                    )
                case "#COMMENT_DELETED":
                    del content_parts[0]
                    content = loc.notification.templates.COMMENT_DELETED(
                        comment_content="\n".join(content_parts)
                    )
                case "#LEADERBOARD_SCORE_DELETED":
                    del content_parts[0]
                    content = loc.notification.templates.LEADERBOARD_SCORE_DELETED(
                        chart_name="\n".join(content_parts)
                    )
                case _:
                    content = self.content

        return post, content