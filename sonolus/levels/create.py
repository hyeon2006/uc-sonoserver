from fastapi import APIRouter
from fastapi import HTTPException, status
from core import SonolusRequest

router = APIRouter()

@router.post("/")
async def main(request: SonolusRequest):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=request.state.loc.use_website_to_upload("https://untitledcharts.com"),
    )