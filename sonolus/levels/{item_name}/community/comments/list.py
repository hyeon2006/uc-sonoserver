from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.sonolus_typings import ItemType

from helpers.models.sonolus.response import ServerItemCommunityCommentList
from helpers.models.sonolus.options import ServerForm
from helpers.models.api.comments import Comment
from helpers.models.sonolus.item import ServerItemCommunityComment
from helpers.models.api.comments import CommentList

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_uwu

import aiohttp

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
    locale: Loc = request.state.loc
    page = request.state.query_params.get("page", 0)
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")
    
    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.get(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/comment/",
            params={"page": page},
        ) as req:
            response = CommentList.model_validate_json(await req.json())

    page_count = response.pageCount
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
    
    comments = response.data
    comment_delete_action = ServerForm(
        type="delete",
        title="#DELETE",
        icon="delete",
        requireConfirmation=True,
        options=[]
    )

    return ServerItemCommunityCommentList(
        pageCount=page_count,
        comments=[process_comment(comment, response.mod, request.state.localization, uwu_level, comment_delete_action) for comment in comments]
    )
