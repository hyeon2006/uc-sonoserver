from fastapi import APIRouter
from fastapi import HTTPException, status
from core import SonolusRequest
from helpers.sonolus_typings import ItemType
from helpers.models.sonolus.item_section import GenericItemSection
from helpers.models.sonolus.response import ServerItemInfo
from helpers.data_compilers import (
    compile_banner,
    compile_backgrounds_list,
    compile_effects_list,
    compile_engines_list,
    compile_particles_list,
    compile_skins_list,
    compile_playlists_list,
)

router = APIRouter()

from helpers.owoify import handle_item_uwu, handle_uwu


@router.get("/", response_model=ServerItemInfo)
async def main(request: SonolusRequest, item_type: ItemType):
    locale = request.state.loc
    uwu_level = request.state.uwu
    banner_srl = await request.app.run_blocking(compile_banner)

    match item_type:
        case "engines":
            data = [
                item.to_engine_item()
                for item in await request.app.run_blocking(
                    compile_engines_list,
                    request.app.base_url,
                    request.state.localization,
                )
            ]
        case "skins":
            data = await request.app.run_blocking(
                compile_skins_list, request.app.base_url
            )
            data = [
                item.to_skin_item()
                for item in data
                if (not item.engines) or (request.state.engine in item.engines)
            ]
        case "backgrounds":
            data = await request.app.run_blocking(
                compile_backgrounds_list,
                request.app.base_url,
                request.state.localization,
            )
        case "effects":
            data = await request.app.run_blocking(
                compile_effects_list, request.app.base_url
            )
        case "particles":
            data = [
                item.to_particle_item()
                for item in await request.app.run_blocking(
                    compile_particles_list, request.app.base_url
                )
            ]
        # case "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        case _:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_type_not_found(item_type),
            )

    return ServerItemInfo(
        sections=[
            GenericItemSection(
                title="#" + item_type[:-1].upper(),
                icon=item_type[:-1],
                description=handle_uwu(
                    locale.server_description or request.app.config["description"],
                    request.state.localization,
                    uwu_level,
                ),
                itemType=item_type[:-1],
                items=handle_item_uwu(
                    data[:5], request.state.localization, request.state.uwu
                ),
            ).model_dump()
        ],
        banner=banner_srl if banner_srl else None,
    )
