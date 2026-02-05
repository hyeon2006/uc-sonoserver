from fastapi import APIRouter
from fastapi import HTTPException, status

from core import SonolusRequest
from helpers.data_compilers import (
    compile_engines_list,
    compile_backgrounds_list,
    compile_effects_list,
    compile_particles_list,
    compile_skins_list,
    # compile_rooms_list
)
from helpers.owoify import handle_item_uwu
from helpers.sonolus_typings import ItemType
from helpers.models.sonolus.response import ServerItemDetails
from helpers.models.sonolus.item import ServerItem

router = APIRouter()


@router.get("/", response_model=ServerItemDetails)
async def main(request: SonolusRequest, item_type: ItemType, item_name: str):
    locale = request.state.loc
    item_data: ServerItem = None

    match item_type:
        case "engines":
            data = [item.to_engine_item() for item in await request.app.run_blocking(
                compile_engines_list, request.app.base_url, request.state.localization
            )]
        case "skins":
            data = [item.to_skin_item() for item in await request.app.run_blocking(compile_skins_list, request.app.base_url)]
        case "backgrounds":
            item_data = (
                await request.app.run_blocking(
                    compile_backgrounds_list,
                    request.app.base_url,
                    request.state.localization,
                )
            )[0]

            if item_data.name != item_name:
                item_data = item_data.model_copy()
                item_data.name = item_name
                item_data.title = item_name.title()
                item_data.subtitle = item_name.title()
        case "effects":
            data = await request.app.run_blocking(
                compile_effects_list, request.app.base_url
            )     
        case "particles":
            data = [item.to_particle_item() for item in await request.app.run_blocking(
                compile_particles_list, request.app.base_url
            )]
        # case "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        case _:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(item_type, item_name),
            )
        
    if not item_data:
        item_data = next((i for i in data if i.name == item_name), None)
        if not item_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(
                    item_type.capitalize().removesuffix("s"), item_name
                ),
            )

    item_data = handle_item_uwu([item_data], request.state.localization, request.state.uwu)[0]

    return ServerItemDetails(
        item=item_data,
        description=item_data.description if hasattr(item_data, "description") and item_data.description else None,
        actions=[],
        hasCommunity=False,
        leaderboards=[],
        sections=[]
    )
