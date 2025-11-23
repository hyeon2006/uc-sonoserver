from fastapi import APIRouter
from fastapi import HTTPException

from core import SonolusRequest

from helpers.models.sonolus.response import ServerItemCommunityCommentList
from helpers.models.sonolus.options import ServerForm
from helpers.models.api.comments import Comment
from helpers.models.sonolus.item import ServerItemCommunityComment

router = APIRouter()

from helpers.owoify import handle_uwu

def process_comment(comment: Comment, is_mod: bool | None, localization, uwu_level, comment_delete_action: ServerForm) -> ServerItemCommunityComment:
    return ServerItemCommunityComment(
        name=str(comment.id),
        author=handle_uwu(
            comment.username,
            localization,
            uwu_level,
            symbols=False
        ),
        time=comment.created_at,
        content=handle_uwu(
            comment.content, localization, uwu_level
        ),
        actions=(
            [comment_delete_action]
            if (comment.owner or is_mod)
            and not comment.deleted_at
            else []
        )
    )

@router.get("/", response_model=ServerItemCommunityCommentList)
async def main(request: SonolusRequest, item_name: str):
    locale = request.state.loc
    page = request.state.query_params.get("page", 0)
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")

    response = await request.app.api.get_comments(item_name, page).send(auth)
    page_count = response.data.pageCount
    if page > page_count or page < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                locale.invalid_page_plural(page, page_count)
                if page_count != 1
                else locale.invalid_page_singular(page, page_count)
            ),
        )
    elif page_count == 0:
        raise HTTPException(status_code=400, detail=locale.not_found)
    
    comments = response.data.data
    comment_delete_action = ServerForm(
        type="delete",
        title="#DELETE",
        icon="delete",
        requireConfirmation=True,
        options=[]
    )

    return ServerItemCommunityCommentList(
        pageCount=page_count,
        comments=[process_comment(comment, response.data.mod, request.state.localization, uwu_level, comment_delete_action) for comment in comments]
    )
