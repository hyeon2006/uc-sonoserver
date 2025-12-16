from fastapi import APIRouter, HTTPException, Query

from core import SonolusRequest
from helpers.models.api.misc import LeaderboardDBResponse
from helpers.models.sonolus.item import ReplayItem
from helpers.models.sonolus.misc import SRL, ServerItemLeaderboardRecord
from helpers.models.sonolus.response import ServerItemLeaderboardDetails, ServerItemLeaderboardRecordDetails, ServerItemLeaderboardRecordList

router = APIRouter()

def generate_string(replay: LeaderboardDBResponse) -> str:
    string = f"{replay.arcade_score} / {replay.accuracy_score} | {replay.nperfect} / {replay.ngreat} / {replay.ngood} / {replay.nmiss}"

    if replay.speed != 1:
        string += f" | {replay.speed}x"

    return string

@router.get("/", response_model=ServerItemLeaderboardDetails)
async def info(item_name: str, request: SonolusRequest):
    response = await request.app.api.get_leaderboards_info(item_name).send(request.headers.get("Sonolus-Session"))

    if response.status != 200:
        raise HTTPException(status_code=response.status)

    top_records = []

    for i, replay in enumerate(response.data.data):
        top_records.append(
            ServerItemLeaderboardRecord(
                name=str(replay.id),
                rank=f"#{i + 1}",
                player=replay.display_name,
                value=generate_string(replay)
            )
        )

    return ServerItemLeaderboardDetails(
        topRecords=top_records
    )

@router.get("/records/list", response_model=ServerItemLeaderboardRecordList)
async def list(item_name: str, request: SonolusRequest, page: int = Query(0, ge=0)):
    response = await request.app.api.get_leaderboards(item_name, page).send(request.headers.get("Sonolus-Session"))

    if response.status != 200:
        raise HTTPException(status_code=response.status)
    
    records = []

    for i, replay in enumerate(response.data.data):
        records.append(
            ServerItemLeaderboardRecord(
                name=str(replay.id),
                rank=f"#{i + ((page - 1) * 10) + 1}",
                player=replay.display_name,
                value=generate_string(replay)
            )
        )

    return ServerItemLeaderboardRecordList(
        pageCount=response.data.pageCount,
        records=records
    )

def make_url(asset_base_url: str, chart_prefix: str, user_id: str, hash: str) -> str:
    return f"{asset_base_url}/{chart_prefix}/replays/{user_id}/{hash}"

@router.get("/records/{name}", response_model=ServerItemLeaderboardRecordDetails)
async def replay_info(item_name: str, name: str, request: SonolusRequest):
    auth = request.headers.get("Sonolus-Session")

    replay_response = await request.app.api.get_record(item_name, int(name)).send(auth)

    if replay_response.status != 200:
        raise HTTPException(status_code=replay_response.status)
    
    level_response = await request.app.api.get_chart(item_name).send(auth)

    if replay_response.status != 200:
        raise HTTPException(status_code=level_response.status)
    
    asset_base_url = level_response.data.asset_base_url.removesuffix("/")

    level = await request.app.run_blocking(
        level_response.data.data.to_level_item,
        request,
        asset_base_url,
        request.state.levelbg, # TODO: remove
    )

    return ServerItemLeaderboardRecordDetails(
        replays=[ReplayItem(
            name=str(replay_response.data.data.id),
            source=request.app.base_url,
            title=generate_string(replay_response.data.data),
            subtitle=level.name,
            author=replay_response.data.data.display_name,
            tags=[],
            level=level,
            data=SRL(
                hash=replay_response.data.data.replay_data_hash,
                url=make_url(asset_base_url, replay_response.data.data.chart_prefix, replay_response.data.data.submitter, replay_response.data.data.replay_data_hash)
            ),
            configuration=SRL(
                hash=replay_response.data.data.replay_config_hash,
                url=make_url(asset_base_url, replay_response.data.data.chart_prefix, replay_response.data.data.submitter, replay_response.data.data.replay_config_hash)
            )
        )]
    )

# TODO: chart -> level ..?
# TODO: replay_to_replayitem
# TODO: message for non-200 responses / handle non-200 somewhere else
# TODO: delete replays or private replays by mod or whatever
# TODO (with backend): replace leaderboard/record/score with a single word