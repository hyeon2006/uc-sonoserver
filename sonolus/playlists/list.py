from fastapi import APIRouter, HTTPException, status

from core import SonolusRequest

router = APIRouter()

@router.get("/")
async def main(request: SonolusRequest):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=request.state.loc.item_not_found("playlists"))