from fastapi import APIRouter, HTTPException, Query

from core import SonolusRequest
from helpers.models.sonolus.response import ServerItemLeaderboardDetails, ServerItemLeaderboardRecordDetails, ServerItemLeaderboardRecordList

router = APIRouter()

@router.get("/", response_model=ServerItemLeaderboardDetails)
async def info(item_name: str, request: SonolusRequest):
    response = await request.app.api.get_leaderboard_info(item_name).send(request.headers.get("Sonolus-Session"))

    if response.status != 200:
        raise HTTPException(status_code=response.status)

    return ServerItemLeaderboardDetails(
        topRecords=await request.app.run_blocking(
            response.data.to_record_list,
            item_name
        )
    )

@router.get("/records/list", response_model=ServerItemLeaderboardRecordList)
async def list(item_name: str, request: SonolusRequest, page: int = Query(1, ge=1)):
    response = await request.app.api.get_leaderboards(item_name, page).send(request.headers.get("Sonolus-Session"))

    if response.status != 200:
        raise HTTPException(status_code=response.status)

    return ServerItemLeaderboardRecordList(
        pageCount=response.data.pageCount,
        records=await request.app.run_blocking(
            response.data.to_record_list,
            item_name,
            page=page
        )
    )

@router.get("/records/{name}", response_model=ServerItemLeaderboardRecordDetails)
async def leaderboard_record_info(item_name: str, name: str, request: SonolusRequest):
    auth = request.headers.get("Sonolus-Session")

    replay_response = await request.app.api.get_leaderboard_record(item_name, int(name)).send(auth)

    if replay_response.status != 200:
        raise HTTPException(status_code=replay_response.status)
    
    chart_response = await request.app.api.get_chart(item_name).send(auth)

    if replay_response.status != 200:
        raise HTTPException(status_code=chart_response.status)
    
    asset_base_url = chart_response.data.asset_base_url.removesuffix("/")

    replay_item = replay_response.data.to_replay_item(
        await request.app.run_blocking(
            chart_response.data.data.to_level_item,
            request,
            asset_base_url,
            request.state.levelbg,
        ),
        request
    )

    return ServerItemLeaderboardRecordDetails(replays=[replay_item])

# TODO: different leaderboard types
# TODO: uwuify | handle_item_uwu([item_data], request.state.localization, request.state.uwu)[0]
# TODO: leaderboards page
# TODO: user type implementation (putting here bc the pile of todos is here)