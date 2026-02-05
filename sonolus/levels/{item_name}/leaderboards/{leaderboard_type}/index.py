from fastapi import APIRouter, HTTPException, Query

from core import SonolusRequest
from helpers.models.api.leaderboards import leaderboard_type
from helpers.models.sonolus.response import ServerItemLeaderboardDetails, ServerItemLeaderboardRecordDetails, ServerItemLeaderboardRecordList
from helpers.owoify import handle_item_uwu

router = APIRouter()

@router.get("/", response_model=ServerItemLeaderboardDetails)
async def info(item_name: str, leaderboard_type: leaderboard_type, request: SonolusRequest):
    response = await request.app.api.get_leaderboard_info(item_name, leaderboard_type).send(request.headers.get("Sonolus-Session"))

    if response.status != 200:
        raise HTTPException(status_code=response.status)

    return ServerItemLeaderboardDetails(
        topRecords=handle_item_uwu(
            await request.app.run_blocking(
                response.data.to_record_list,
                leaderboard_type
            ),
            request.state.localization,
            request.state.uwu
        )
    )

@router.get("/records/list", response_model=ServerItemLeaderboardRecordList)
async def list(item_name: str, leaderboard_type: leaderboard_type, request: SonolusRequest, page: int = Query(0, ge=0)):
    response = await request.app.api.get_leaderboards(item_name, leaderboard_type, page).send(request.headers.get("Sonolus-Session"))

    if response.status != 200:
        raise HTTPException(status_code=response.status)

    return ServerItemLeaderboardRecordList(
        pageCount=response.data.pageCount,
        records=handle_item_uwu(
            await request.app.run_blocking(
                response.data.to_record_list,
                leaderboard_type,
                page=page
            ),
            request.state.localization,
            request.state.uwu
        )
    )

@router.get("/records/{name}", response_model=ServerItemLeaderboardRecordDetails)
async def leaderboard_record_info(item_name: str, name: str, request: SonolusRequest):
    auth = request.headers.get("Sonolus-Session")

    replay_response = await request.app.api.get_leaderboard_record(item_name, int(name.rsplit("-", maxsplit=1)[-1])).send(auth)

    if replay_response.status != 200:
        raise HTTPException(status_code=replay_response.status)

    replay_item = await request.app.run_blocking(
        replay_response.data.to_replay_item,
        request
    )

    return ServerItemLeaderboardRecordDetails(replays=handle_item_uwu([replay_item], request.state.localization, request.state.uwu))
