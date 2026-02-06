from fastapi import APIRouter, File, HTTPException, Header, UploadFile, status

from core import SonolusRequest
import helpers.replay as replay

router = APIRouter()

MAX_FILE_SIZES = {"data": 2 * 1024 * 1024, "config": 1024}  # 2 mb / 1 mb


@router.post("/")
async def upload(
    request: SonolusRequest,
    upload_key: str = Header(alias="Sonolus-Upload-Key"),
    files: list[UploadFile] = File(...),
):
    files_map = {file.filename: file for file in files}
    data = replay.verify_upload_key(upload_key, request)

    replay_data = await files_map[data.data_hash].read()
    replay_configuration = await files_map[data.configuration_hash].read()

    if (
        len(replay_data) > MAX_FILE_SIZES["data"]
        or len(replay_configuration) > MAX_FILE_SIZES["config"]
    ):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Uploaded files exceed file size limit.",
        )

    info = replay.validate_replay_config(
        replay_configuration, data.engine_name, request
    )

    response = await request.app.api.upload_replay(
        replay_data,
        replay_configuration,
        data.chart_name,
        data.user_id,
        data.display_name,
        data.engine_name,
        info.speed,
    ).send()

    if response.status != 200:
        raise HTTPException(
            status_code=response.status, detail=request.state.loc.unknown_error
        )

    return {}
