from fastapi import APIRouter, HTTPException

from core import SonolusRequest
from helpers.models.sonolus.options import ServerForm
from helpers.models.sonolus.response import ServerItemDetails

router = APIRouter()

@router.get("/")
async def get(request: SonolusRequest, item_name: str):
    chart_name, record_id = item_name.removesuffix("UnCh-").split("-")
    auth = request.headers.get("Sonolus-Session")

    leaderboard_record_response = await request.app.api.get_leaderboard_record(chart_name, int(record_id)).send(auth)

    if leaderboard_record_response.status != 200:
        raise HTTPException(status_code=leaderboard_record_response.status)
    
    chart_response = await request.app.api.get_chart(item_name).send(auth)

    if leaderboard_record_response.status != 200:
        raise HTTPException(status_code=chart_response.status)
    
    asset_base_url = chart_response.data.asset_base_url.removesuffix("/")

    replay_item = leaderboard_record_response.data.to_replay_item(
        await request.app.run_blocking(
            chart_response.data.data.to_level_item,
            request,
            asset_base_url,
            request.state.levelbg,
        ),
        request
    )

    actions = [
        ServerForm(
            type="delete",
            title="#DELETE",
            icon="delete",
            requireConfirmation=True
        )
    ] if leaderboard_record_response.data.data.owner or leaderboard_record_response.data.data.mod else []

    return ServerItemDetails(
        item=replay_item,
        actions=actions,
        hasCommunity=False,
        leaderboards=[],
        sections=[]
    )