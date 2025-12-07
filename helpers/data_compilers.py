import gzip, json, os
from io import BytesIO

from typing import Optional, List
from helpers.datastructs import (
    EngineItem,
    SRL,
    SkinItem,
    BackgroundItem,
    EffectItem,
    ParticleItem,
    PostItem,
    PlaylistItem,
)

from helpers.repository_map import repo

from locales.locale import Locale

cached = {
    "skins": None,
    "effects": None,
    "particles": None,
    "banner": None,
    "static_posts": None,
    "BACKGROUND_NO_SCOPE_SRL": None,
}


def clear_compile_cache(specific: str = None):
    global cached
    if specific:
        cached[specific] = None
    else:
        new_cached = {}
        for k in cached.keys():
            new_cached[k] = None
        cached = new_cached.copy()


def compile_banner() -> Optional[SRL]:
    if cached["banner"]:
        return cached["banner"]
    path = "files/banner/banner.png"
    if os.path.exists(path):
        hash = repo.add_file(path)
        return repo.get_srl(hash)
    return None


def compile_playlists_list(
    source: str = None, locale: str = "en"
) -> List[PlaylistItem]:
    loc, locale = Locale.get_messages(locale)
    if cached.get(f"playlists_{locale}"):
        return cached[f"playlists_{locale}"]
    compiled_data_list = []
    for playlist in os.listdir("files/playlists"):
        if not os.path.isdir(os.path.join("files", "playlists", playlist)):
            continue
        compiled_data: PlaylistItem = {"tags": [], "levels": []}
        compiled_data["name"] = playlist
        if source:
            compiled_data["source"] = source
        with open(
            f"files/playlists/{playlist}/playlist.json", "r", encoding="utf8"
        ) as f:
            post_data: dict = json.load(f)
        if not post_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            k_value = post_data[key]
            if type(k_value) == str:
                k_value = (
                    k_value.replace("#YOU", loc.you)
                    .replace("#UPLOADEDSUB", loc.playlist.UPLOADEDSUB)
                    .replace("#UPLOADED", loc.playlist.UPLOADED)
                )
            compiled_data[key] = k_value
        data_files = {"thumbnail": "thumbnail.png"}
        for key, file in data_files.items():
            hash = repo.add_file(
                f"files/playlists/{playlist}/{file}", error_on_file_nonexistent=False
            )
            if hash:
                compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached[f"playlists_{locale}"] = compiled_data_list
    return compiled_data_list


def compile_static_posts_list(source: str = None) -> List[PostItem]:
    if cached["static_posts"]:
        return cached["static_posts"]
    compiled_data_list = []
    for post in os.listdir("files/posts"):
        if not os.path.isdir(os.path.join("files", "posts", post)):
            continue
        compiled_data: PostItem = {"tags": []}
        compiled_data["name"] = post
        if source:
            compiled_data["source"] = source
        with open(f"files/posts/{post}/post.json", "r", encoding="utf8") as f:
            post_data: dict = json.load(f)
        if not post_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "time", "author", "description"]
        for key in item_keys:
            compiled_data[key] = post_data[key]
        data_files = {"thumbnail": "thumbnail.png"}
        for key, file in data_files.items():
            hash = repo.add_file(
                f"files/posts/{post}/{file}", error_on_file_nonexistent=False
            )
            if hash:
                compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["static_posts"] = compiled_data_list
    return compiled_data_list


def sort_posts_by_newest(posts: List[PostItem]) -> List[PostItem]:
    return sorted(posts, key=lambda post: post["time"], reverse=True)


def compile_effects_list(source: str = None) -> List[EffectItem]:
    if cached["effects"]:
        return cached["effects"]
    compiled_data_list = []
    for effect in os.listdir("files/effects"):
        if not os.path.isdir(os.path.join("files", "effects", effect)):
            continue
        compiled_data: EffectItem = {"tags": []}
        compiled_data["name"] = effect
        if source:
            compiled_data["source"] = source
        with open(f"files/effects/{effect}/effect.json", "r", encoding="utf8") as f:
            effect_data: dict = json.load(f)
        if not effect_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = effect_data[key]
        data_files = {"thumbnail": "thumbnail.png", "data": "data", "audio": "audio"}
        for key, file in data_files.items():
            hash = repo.add_file(f"files/effects/{effect}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["effects"] = compiled_data_list
    return compiled_data_list


def compile_backgrounds_list(
    source: str = None,
    locale: str = "en",
) -> List[BackgroundItem]:
    loc, locale = Locale.get_messages(locale)
    if cached.get(f"backgrounds_{locale}"):
        return cached[f"backgrounds_{locale}"]
    compiled_data_list = []
    for background in os.listdir("files/backgrounds"):
        if not os.path.isdir(os.path.join("files", "backgrounds", background)):
            continue
        compiled_data: BackgroundItem = {"tags": []}
        compiled_data["name"] = background
        if source:
            compiled_data["source"] = source
        with open(
            f"files/backgrounds/{background}/background.json", "r", encoding="utf8"
        ) as f:
            background_data: dict = json.load(f)
        if not background_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            d_value = background_data[key]
            if type(d_value) == str:
                d_value = d_value.replace(
                    "#BACKGROUNDSELECTSUB", loc.background.BACKGROUNDSELECTSUB
                ).replace("#BACKGROUNDSELECT", loc.background.BACKGROUNDSELECT)
            compiled_data[key] = d_value
        data_files = {
            "thumbnail": "thumbnail.png",
            "data": "data",
            "image": "image.png",
            "configuration": "configuration.json.gz",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/backgrounds/{background}/{file}")
            compiled_data[key] = repo.get_srl(hash)
            if key == "configuration" and background == "PLEASE-SELECT":
                if not cached["BACKGROUND_NO_SCOPE_SRL"]:
                    with gzip.open(f"files/backgrounds/{background}/{file}", "rb") as f:
                        data = json.load(f)
                    if "scope" in data:
                        del data["scope"]
                    output_buffer = BytesIO()
                    with gzip.GzipFile(fileobj=output_buffer, mode="wb") as gz_out:
                        gz_out.write(json.dumps(data).encode("utf-8"))
                    gzipped_bytes = output_buffer.getvalue()
                    no_scope_hash = repo.add_bytes(gzipped_bytes)
                    cached["BACKGROUND_NO_SCOPE_SRL"] = repo.get_srl(no_scope_hash)
        compiled_data_list.append(compiled_data)
    cached[f"backgrounds_{locale}"] = compiled_data_list
    return compiled_data_list


def compile_particles_list(source: str = None) -> List[ParticleItem]:
    if cached["particles"]:
        return cached["particles"]
    compiled_data_list = []
    for particle in os.listdir("files/particles"):
        if not os.path.isdir(os.path.join("files", "particles", particle)):
            continue
        compiled_data: ParticleItem = {"tags": []}
        compiled_data["name"] = particle
        if source:
            compiled_data["source"] = source
        with open(
            f"files/particles/{particle}/particle.json", "r", encoding="utf8"
        ) as f:
            particle_data: dict = json.load(f)
        if not particle_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "subtitle", "author", "engine_specific"]
        for key in item_keys:
            compiled_data[key] = particle_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "data": "data",
            "texture": "texture",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/particles/{particle}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["particles"] = compiled_data_list
    return compiled_data_list


def compile_skins_list(source: str = None) -> List[SkinItem]:
    if cached["skins"]:
        return cached["skins"]
    compiled_data_list = []
    for skin in os.listdir("files/skins"):
        if not os.path.isdir(os.path.join("files", "skins", skin)):
            continue
        compiled_data: SkinItem = {"tags": []}
        compiled_data["name"] = skin
        if source:
            compiled_data["source"] = source
        with open(f"files/skins/{skin}/skin.json", "r", encoding="utf8") as f:
            skin_data: dict = json.load(f)
        if not skin_data.get("enabled", True):
            continue
        item_keys = [
            "version",
            "title",
            "subtitle",
            "author",
            "engines",
            "themes",
            "locale",
        ]
        for key in item_keys:
            if key in skin_data.keys():
                compiled_data[key] = skin_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "data": "data",
            "texture": "texture",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/skins/{skin}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    compiled_data_list = sorted(compiled_data_list, key=lambda d: d["title"])
    cached["skins"] = compiled_data_list
    return compiled_data_list


def compile_engines_list(source: str = None, locale: str = "en") -> List[EngineItem]:
    if cached.get(f"engines_{locale}"):
        return cached[f"engines_{locale}"]
    compiled_data_list = []
    for engine in os.listdir("files/engines"):
        if not os.path.isdir(os.path.join("files", "engines", engine)):
            continue
        compiled_data: EngineItem = {
            "tags": [],
            "actions": [],
            "hasCommunity": False,
            "leaderboards": [],
            "sections": [],
        }
        with open(f"files/engines/{engine}/engine.json", "r", encoding="utf8") as f:
            engine_data: dict = json.load(f)
        if not engine_data.get("enabled", True):
            continue
        if engine_data.get("description"):
            compiled_data["description"] = engine_data["description"]
        compiled_data["name"] = engine
        if source:
            compiled_data["source"] = source
        item_keys = ["version", "title", "subtitle", "author", "engine_sort_order"]
        for key in item_keys:
            if key in engine_data.keys():
                compiled_data[key] = engine_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "configuration": "EngineConfiguration",
            "playData": "EnginePlayData",
            "watchData": "EngineWatchData",
            "previewData": "EnginePreviewData",
            "tutorialData": "EngineTutorialData",
            "rom": "EngineRom",
        }
        for key, file in data_files.items():
            if key != "configuration":
                if os.path.exists(f"files/engines/{engine}/{file}"):
                    hash = repo.add_file(f"files/engines/{engine}/{file}")
                    compiled_data[key] = repo.get_srl(hash)
            else:
                if os.path.exists(f"files/engines/{engine}/{file}"):
                    config_overrides = engine_data.get("config_overrides", {})
                    if config_overrides:
                        with gzip.open(
                            f"files/engines/{engine}/{file}", "rt", encoding="utf-8"
                        ) as f:
                            data = json.load(f)
                        for option in data.get("options", []):
                            option_name = option.get("name")
                            if option_name in config_overrides.keys():
                                for opt_key, value in config_overrides[
                                    option_name
                                ].items():
                                    option[opt_key] = value
                        bytes_io = BytesIO()
                        with gzip.GzipFile(fileobj=bytes_io, mode="wb") as gzipped_file:
                            json_data = json.dumps(data, ensure_ascii=False).encode(
                                "utf-8"
                            )
                            gzipped_file.write(json_data)
                        bytes_io.seek(0)
                        hash = repo.add_bytes(bytes_io.read())
                        compiled_data[key] = repo.get_srl(hash)
                    else:
                        hash = repo.add_file(f"files/engines/{engine}/{file}")
                        compiled_data[key] = repo.get_srl(hash)

        def get_skin_name(engine_data: dict, locale: str) -> str:
            if engine_data.get("skin_name_locale", {}).get(locale):
                return engine_data["skin_name_locale"][locale]
            return engine_data["skin_name"]

        try:
            skins = compile_skins_list(source)
            skin_data = next(
                skin
                for skin in skins
                if skin["name"] == get_skin_name(engine_data, locale)
            )
            compiled_data["skin"] = skin_data
            effects = compile_effects_list(source)
            effect_data = next(
                effect
                for effect in effects
                if effect["name"] == engine_data["effect_name"]
            )
            compiled_data["effect"] = effect_data
            particles = compile_particles_list(source)
            particle_data = next(
                particle
                for particle in particles
                if particle["name"] == engine_data["particle_name"]
            )
            compiled_data["particle"] = particle_data
            backgrounds = compile_backgrounds_list(source, locale)
            background_data = next(
                background
                for background in backgrounds
                if background["name"] == engine_data["background_name"]
            )
            compiled_data["background"] = background_data
        except StopIteration:
            raise KeyError(
                "StopIteration raised: incorrect key name! Make sure your engine file names and resource file names match."
            )
        compiled_data_list.append(compiled_data)
    compiled_data_list = sorted(
        compiled_data_list,
        key=lambda item: (
            item.get("engine_sort_order", float("inf")),  # last, if no sort order
            item["title"].lower(),  # abc
        ),
    )
    cached[f"engines_{locale}"] = compiled_data_list
    return compiled_data_list
