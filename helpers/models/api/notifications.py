from datetime import datetime
from pydantic import BaseModel
from core import SonolusRequest
from helpers.models.sonolus.item import PostItem
from helpers.models.sonolus.misc import Tag

class _BaseNotification(BaseModel):
    id: int
    title: str
    is_read: bool = False
    created_at: datetime = None
    timestamp: int # TODO (backend): remove timestamp (need to check frontend tho)

    def to_post(self, request: SonolusRequest) -> PostItem:
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
        posts = []

        for notification in self.notifications:
            posts.append(notification.to_post(request))

class Notification(_BaseNotification):
    user_id: str
    content: str


    def to_post(self, request: SonolusRequest) -> tuple[PostItem, str]:
        post = super().to_post(request)
        loc = request.state.loc

        content_parts = self.content.splitlines()
        if content_parts[0].startswith("#"):
            del content_parts[0]

            match content_parts[0]:
                case "#CHART_DELETED":
                    content = loc.notification.templates.CHART_DELETED(
                        chart_name="\n".join(content_parts)
                    )
                case "#CHART_VISIBILITY_CHANGED":
                    content = loc.notification.templates.CHART_VISIBILITY_CHANGED(
                        visibility_status=content_parts.pop(0), chart_name="\n".join(content_parts)
                    )
                case "#COMMENT_DELETED":
                    content = loc.notification.templates.COMMENT_DELETED(
                        comment_content="\n".join(content_parts)
                    )
                case _:
                    content = self.content

        return post, content