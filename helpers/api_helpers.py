from typing import Any, Dict

from functools import lru_cache
from helpers.data_compilers import (
    compile_engines_list,
    compile_backgrounds_list,
    compile_particles_list,
    compile_skins_list,
)
from locales.locale import Loc
from helpers.owoify import handle_uwu
from datetime import datetime, timedelta, timezone


def api_notif_to_post(
    request,
    i: dict,
    include_description: bool = False,
) -> dict | tuple:
    loc: Loc = request.state.loc
    d = {
        "name": f"notification-{i['id']}",
        "source": request.app.base_url,
        "version": 1,
        "title": i["title"],
        "time": i["timestamp"],
        "author": "UntitledCharts",
        "tags": [
            (
                {"title": loc.notification.READ_STATUS, "icon": "envelopeOpen"}
                if i["is_read"]
                else {"title": loc.notification.UNREAD_STATUS, "icon": "envelope"}
            )
        ],
    }
    if include_description:
        content = i["content"]
        content_parts = content.splitlines()
        if content_parts[0].startswith("#"):
            if content_parts[0] == "#CHART_DELETED":
                del content_parts[0]
                content = loc.notification.templates.CHART_DELETED(
                    chart_name="\n".join(content_parts)
                )
            elif content_parts[0] == "#CHART_VISIBILITY_CHANGED":
                del content_parts[0]
                visibility = content_parts.pop(0)
                content = loc.notification.templates.CHART_VISIBILITY_CHANGED(
                    visibility_status=visibility, chart_name="\n".join(content_parts)
                )
            elif content_parts[0] == "#COMMENT_DELETED":
                del content_parts[0]
                content = loc.notification.templates.COMMENT_DELETED(
                    comment_content="\n".join(content_parts)
                )
        return d, content
    return d


def api_level_to_level(
    request,
    asset_base_url: str,
    i: dict,
    bgtype: str,
    include_description: bool = False,
    disable_replace_missing_preview: bool = False,
    context: str = "list",  # or level
) -> dict | tuple:
    loc: Loc = request.state.loc

    @lru_cache(maxsize=None)
    def get_cached_particle(base_url: str, particle_name: str):
        particles = compile_particles_list(base_url)
        particle_data = next(
            particle for particle in particles if particle["name"] == particle_name
        )
        return particle_data

    @lru_cache(maxsize=None)
    def get_cached_skin(
        base_url: str, skin_name: str, engine_name: str, localization: str
    ) -> Dict[str, Any]:
        skins = compile_skins_list(base_url)

        candidates = [
            skin
            for skin in skins
            if skin_name in skin.get("themes", [])
            and ("engines" not in skin or engine_name in skin["engines"])
        ]

        if not candidates:
            raise KeyError("no matching theme/engine for skin found")

        #  try to match locale
        for skin in candidates:
            if skin.get("locale") == localization:
                return skin

        # fallback: find skin where no locale is set (some global skin)
        for skin in candidates:
            if skin.get("locale") == None:
                return skin

        # fallback 2: just return first item
        return candidates[0]

    @lru_cache(maxsize=None)
    def get_cached_background(base_url: str, localization: str):
        return compile_backgrounds_list(base_url, localization)[0].copy()

    @lru_cache(maxsize=None)
    def get_cached_engine(base_url: str, engine_name: str, locale: str):
        engines = compile_engines_list(base_url, locale)
        engine_data = next(
            engine for engine in engines if engine["name"] == engine_name
        )
        return engine_data

    author = i["author"]
    level_id = i["id"]

    def make_url(file_hash: str) -> str:
        return "/".join([asset_base_url, author, level_id, file_hash])

    default = bgtype.startswith("default_or_")
    if default:
        bgtype = bgtype.removeprefix("default_or_")
        background_hash = i.get("background_file_hash")
    else:
        background_hash = None

    if not background_hash:
        default = False
        background_hash = i[f"background_{bgtype}_file_hash"]

    bg_item = get_cached_background(request.app.base_url, request.state.localization)
    bg_item["image"] = {"hash": background_hash, "url": make_url(background_hash)}
    bg_item["thumbnail"] = {
        "hash": i["jacket_file_hash"],
        "url": make_url(i["jacket_file_hash"]),
    }
    bg_item["name"] = "configured"
    if not default and bgtype == "v3":
        title = loc.background.V3
    elif not default and bgtype == "v1":
        title = loc.background.V1
    else:
        title = loc.background.UPLOADED
    bg_item["title"] = handle_uwu(title, request.state.localization, request.state.uwu)

    if request.state.skin == "engine_default":
        skin_option = {"useDefault": True}
    else:
        try:
            skin_option = {
                "useDefault": False,
                "item": get_cached_skin(
                    request.app.base_url,
                    request.state.skin,
                    request.state.engine,
                    request.state.localization,
                ),
            }
        except:  # handles if an engine does not have a correctly-themed skin, KeyError
            skin_option = {"useDefault": True}

    if request.state.particle == "engine_default":
        particle_option = {"useDefault": True}
    else:
        try:
            particle_option = {
                "useDefault": False,
                "item": get_cached_particle(
                    request.app.base_url, request.state.particle
                ),
            }
        except:
            particle_option = {"useDefault": True}

    if i.get("published_at"):
        key = "published_at"
    else:
        key = "created_at"
    created_at = datetime.fromisoformat(i[key].rstrip("Z")).astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - created_at
    if delta >= timedelta(days=1):
        days = delta.days
        time_str = f"{days}d"
    elif delta >= timedelta(hours=1):
        hours = delta.seconds // 3600
        time_str = f"{hours}h"
    elif delta >= timedelta(minutes=1):
        minutes = delta.seconds // 60
        time_str = f"{minutes}m"
    elif delta >= timedelta(seconds=1):
        seconds = delta.seconds
        time_str = f"{seconds}s"
    else:
        time_str = "0s"
    created_at_str = handle_uwu(
        (
            loc.time_ago(time_str)
            if key == "published_at"
            else loc.time_ago_not_published(time_str)
        ),
        request.state.localization,
        request.state.uwu,
    )

    if context == "list":
        additional = []
        tags = [
            {"title": handle_uwu(tag, request.state.localization, request.state.uwu)}
            for tag in i["tags"]
        ]
    elif context == "level":
        VISIBILITIES = {
            "PUBLIC": {"title": "#PUBLIC", "icon": "globe"},
            "PRIVATE": {"title": "#PRIVATE", "icon": "lock"},
            "UNLISTED": {
                "title": loc.search.VISIBILITY_UNLISTED,
                "icon": "unlock",
            },
        }
        additional = [
            {
                "title": VISIBILITIES[i["status"]]["title"],
                "icon": VISIBILITIES[i["status"]]["icon"],
            }
        ]
        tags = [
            {
                "title": handle_uwu(tag, request.state.localization, request.state.uwu),
                "icon": "tag",
            }
            for tag in i["tags"]
        ]

    metadata = [
        {"title": created_at_str, "icon": "clock"},
        {
            "title": str(i["like_count"]),
            "icon": "heart" if i.get("liked") else "heartHollow",
        },
        {
            "title": str(i["comment_count"]),
            "icon": "comment",
        },
    ]

    leveldata = {
        "name": f"UnCh-{level_id}",
        "source": request.app.base_url,
        "version": 1,
        "rating": i["rating"],
        "artists": handle_uwu(
            i["artists"], request.state.localization, request.state.uwu
        ),
        "author": i["author_full"],
        "title": handle_uwu(i["title"], request.state.localization, request.state.uwu),
        "tags": (additional + metadata + tags),
        "engine": get_cached_engine(
            request.app.base_url, request.state.engine, request.state.localization
        ),
        "useSkin": skin_option,
        "useEffect": {"useDefault": True},
        "useParticle": particle_option,
        "useBackground": {"useDefault": False, "item": bg_item},
        "cover": {
            "hash": i["jacket_file_hash"],
            "url": make_url(i["jacket_file_hash"]),
        },
        "data": {"hash": i["chart_file_hash"], "url": make_url(i["chart_file_hash"])},
        "bgm": {"hash": i["music_file_hash"], "url": make_url(i["music_file_hash"])},
    }

    if i.get("preview_file_hash"):
        leveldata["preview"] = {
            "hash": i["preview_file_hash"],
            "url": make_url(i["preview_file_hash"]),
        }
    elif not disable_replace_missing_preview:
        leveldata["preview"] = {
            "hash": i["music_file_hash"],
            "url": make_url(i["music_file_hash"]),
        }

    if i["staff_pick"]:
        if context == "list":
            leveldata["tags"].insert(
                0,
                {
                    "title": "",
                    "icon": "trophy",
                },
            )
        elif context == "level":
            leveldata["tags"].insert(
                0,
                {
                    "title": loc.staff_pick,
                    "icon": "trophy",
                },
            )

    if not include_description:
        return leveldata
    else:
        desc = i.get("description")
        if desc:
            desc = handle_uwu(desc, request.state.localization, request.state.uwu)
        return leveldata, desc
