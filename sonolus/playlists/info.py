from fastapi import APIRouter

from core import SonolusRequest
from helpers.data_compilers import compile_banner, compile_playlists_list
from helpers.models.sonolus.item_section import PlaylistItemSection
from helpers.models.sonolus.response import ServerItemInfo
from helpers.owoify import handle_item_uwu, handle_uwu

router = APIRouter()

@router.get("/", response_model=ServerItemInfo)
async def main(request: SonolusRequest):
    locale = request.state.loc
    uwu_level = request.state.uwu
    banner_srl = await request.app.run_blocking(compile_banner)

    data = await request.app.run_blocking(
        compile_playlists_list, request.app.base_url, request.state.localization
    )

    return ServerItemInfo(
        sections=[
            PlaylistItemSection(
                title="#PLAYLIST",
                icon="playlist",
                description=handle_uwu(
                    locale.server_description or request.app.config["description"],
                    request.state.localization,
                    uwu_level,
                ),
                items=handle_item_uwu(data[:5], request.state.localization, request.state.uwu)
            )
        ],
        banner=banner_srl if banner_srl else None
    )
