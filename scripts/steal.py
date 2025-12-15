"""
Steals staff-picked levels from unch and uploads to the local fork (needs enabled debug)

Requires requests and tqdm: pip install requests, tqdm
run from the uc-sonoserver directory, python3 -m scripts.steal http://127.0.0.1:8001

..please use for tests only..
"""

import requests
import json
from io import BytesIO
from helpers.models.api.levels import LevelList
from tqdm import tqdm
from sys import argv

request = requests.get("https://sono_api.untitledcharts.com/api/charts?staff_pick=1&type=advanced&sort_by=published_at", verify=False)
levels = LevelList.model_validate(request.json())

def make_url(author: str, id: str, asset_base_url: str, file_hash: str) -> str:
    return "/".join([asset_base_url, author, id, file_hash])

def download(link: str) -> BytesIO:
    request = requests.get(link)

    io = BytesIO(request.content)
    io.seek(0)

    return io

external_auth_id = requests.post(f"{argv[1]}/api/accounts/session/external/id/").json()["id"]
session = requests.post(
    f"{argv[1]}/api/accounts/session/external/",
    json={
        "id": "buuecq3cbgku8mjbl0ii1almkrt812zvg52bg4zfbek1kjiwyqtv32tx4wtzevws",  # random
        "handle": "111111",
        "name": "test user",
        "avatarType": "default",
        "avatarForegroundType": "player",
        "avatarForegroundColor": "#ffffffff",
        "avatarBackgroundType": "default",
        "avatarBackgroundColor": "#000020ff",
        "bannerType": "none",
        "aboutMe": "hii",
        "favorites": [],
        "type": "external",
        "id_key": external_auth_id,
    },
).json()["session"]

for level in tqdm(levels.data):
    data = json.dumps({
        "rating": level.rating,
        "title": level.title,
        "artists": level.artists,
        "author": level.chart_design,
        "includes_background": False,
        "includes_preview": False,
        "tags": level.tags
    })

    request = requests.post(
        f"{argv[1]}/api/charts/upload/",
        data={
            "data": data
        },
        files={
            "jacket_image": ("jacket.png", download(make_url(level.author, level.id, levels.asset_base_url, level.jacket_file_hash))),
            "chart_file": ("chart", download(make_url(level.author, level.id, levels.asset_base_url, level.chart_file_hash))),
            "audio_file": ("audio.mp3", download(make_url(level.author, level.id, levels.asset_base_url, level.music_file_hash)))
        },
        headers={
            "authorization": session
        }
    )

    if request.status_code != 200:
        raise Exception(request.text)