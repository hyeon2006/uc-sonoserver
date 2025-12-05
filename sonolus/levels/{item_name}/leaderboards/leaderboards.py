from fastapi import APIRouter, HTTPException, Query

from core import SonolusRequest
from helpers.models.api.misc import LeaderboardDBResponse
from helpers.models.sonolus.misc import ServerItemLeaderboardRecord
from helpers.models.sonolus.response import ServerItemLeaderboardDetails, ServerItemLeaderboardRecordList

router = APIRouter()

def generate_string(replay: LeaderboardDBResponse) -> str: # TODO: localize.. maybe?
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
                name=replay.id,
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
                name=replay.id,
                rank=f"#{i + ((page - 1) * 10) + 1}",
                player=replay.display_name,
                value=generate_string(replay)
            )
        )

    return ServerItemLeaderboardRecordList(
        pageCount=response.data.pageCount,
        records=records
    )

# TODO: delete replays or private replays by mod or whatever