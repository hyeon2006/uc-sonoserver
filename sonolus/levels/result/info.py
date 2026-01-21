from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def main():
    submit_form = { # TODO: to model
        "type": "replay",
        "title": "#REPLAY",
        "requireConfirmation": False,
        "options": [],
    }
    data = {"submits": [submit_form]}
    return data
