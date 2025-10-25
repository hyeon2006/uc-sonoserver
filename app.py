import os, importlib, asyncio
from urllib.parse import urlparse

from concurrent.futures import ThreadPoolExecutor

import yaml

with open("config.yml", "r") as f:
    config = yaml.load(f, yaml.Loader)

from fastapi import FastAPI, Request
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from helpers.repository_map import repo
from helpers.data_compilers import (
    compile_particles_list,
    compile_engines_list,
    compile_skins_list,
)
from locales.locale import Locale

debug = config["server"]["debug"]


class SonolusFastAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = kwargs["debug"]

        self.executor = ThreadPoolExecutor(max_workers=16)

        self.config = config["sonolus"]
        self.api_config = config["api"]
        self.base_url = kwargs["base_url"]

        self.auth = self.api_config["auth"]
        self.auth_header = self.api_config["auth-header"]

        self.remove_config_queries = [
            "localization",
            "page",
            "uwu",
            "levelbg",
            "stpickconfig",
            "defaultparticle",
            "defaultengine",
            "defaultskin",
        ]

        self.repository = repo

        self.exception_handlers.setdefault(HTTPException, self.http_exception_handler)

    async def run_blocking(self, func, *args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, lambda: func(*args, **kwargs)
        )

    def get_items_per_page(self, route: str) -> int:
        return self.config["items-per-page"].get(
            route, self.config["items-per-page"].get("default")
        )

    async def http_exception_handler(self, request: Request, exc: HTTPException):
        if exc.status_code < 500:
            return JSONResponse(
                content={"message": exc.detail}, status_code=exc.status_code
            )
        else:
            print(
                "-" * 1000
                + f"\nerror 500: {request.method} {str(request.url)}\n"
                + "-" * 1000
            )
            return JSONResponse(content={}, status_code=exc.status_code)


VERSION_REGEX = r"^\d+\.\d+\.\d+$"


class SonolusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.localization = request.query_params.get(
            "localization", "en"
        ).lower()
        uwu_supported = ["tr", "en"]
        request.state.uwu = (
            request.query_params.get("uwu", "off").lower()
            if request.state.localization in uwu_supported
            else "off"
        )
        request.state.levelbg = request.query_params.get(
            "levelbg", "default_or_v3"
        ).lower()
        request.state.staff_pick = request.query_params.get(
            "stpickconfig", "off"
        ).lower()
        request.state.particle = request.query_params.get(
            "defaultparticle", "engine_default"
        ).lower()
        request.state.skin = request.query_params.get("defaultskin", "engine_default")
        skins = await request.app.run_blocking(compile_skins_list, request.app.base_url)
        supported_skins = list(set(theme for skin in skins for theme in skin["themes"]))
        engines = await request.app.run_blocking(
            compile_engines_list, request.app.base_url, request.state.localization
        )
        request.state.engine = request.query_params.get(
            "defaultengine", engines[0]["name"]
        )
        request.state.loc, request.state.localization = Locale.get_messages(
            request.state.localization
        )
        if not request.state.levelbg in [
            "default_or_v3",
            "default_or_v1",
            "v1",
            "v3",
        ]:
            request.state.levelbg = "default_or_v3"
        if not request.state.uwu in ["off", "uwu", "owo", "uvu"]:
            request.state.uwu = "off"
        if not request.state.staff_pick in ["off", "true", "false"]:
            request.state.staff_pick = "off"
        particles = await request.app.run_blocking(
            compile_particles_list, request.app.base_url
        )
        if not request.state.particle in [
            "engine_default",
            *[item["name"] for item in particles],
        ]:
            request.state.particle = "engine_default"
        if not request.state.engine in [item["name"] for item in engines]:
            request.state.engine = engines[0]["name"]
        if not request.state.skin in ["engine_default", *supported_skins]:
            request.state.skin = "engine_default"
            # return JSONResponse(
            #     content={"message": "Invalid configuration"},
            #     status_code=status.HTTP_400_BAD_REQUEST,
            # )
        query_params = dict(request.query_params)
        for item in request.app.remove_config_queries:
            query_params.pop(item, None)
        request.state.query_params = query_params
        response = await call_next(request)
        response.headers["Sonolus-Version"] = request.app.config[
            "required-client-version"
        ]
        return response


app = SonolusFastAPI(debug=debug, base_url=config["server"]["base-url"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SonolusMiddleware)
if not debug:
    domain = urlparse(config["server"]["base-url"]).netloc
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[domain])


@app.middleware("http")
async def force_https_redirect(request, call_next):
    response = await call_next(request)

    if config["server"]["force-https"] and not debug:
        if response.headers.get("Location"):
            response.headers["Location"] = response.headers.get("Location").replace(
                "http://", "https://", 1
            )

    return response


# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")


import os
import shutil
import importlib


def load_routes(folder, cleanup: bool = True):
    global app
    """Load Routes from the specified directory."""

    routes = []

    def traverse_directory(directory):
        for root, dirs, files in os.walk(directory, topdown=False):
            for file in files:
                if not "__pycache__" in root and file.endswith(".py"):
                    route_name: str = (
                        os.path.join(root, file)
                        .removesuffix(".py")
                        .replace("\\", "/")
                        .replace("/", ".")
                    )

                    # Check if the route is dynamic or static
                    if "{" in route_name and "}" in route_name:
                        routes.append((route_name, False))  # Dynamic route
                    else:
                        routes.append((route_name, True))  # Static route

    traverse_directory(folder)

    # static first, then dynamic. Deeper routes first.
    routes.sort(key=lambda x: (not x[1], x[0]))

    for route_name, is_static in routes:
        try:
            route = importlib.import_module(route_name)
        except NotImplementedError:
            continue

        route_version = route_name.split(".")[0]
        route_name_parts = route_name.split(".")

        # it's the index for the route
        if route_name.endswith(".index"):
            del route_name_parts[-1]

        route_name = ".".join(route_name_parts)
        app.include_router(
            route.router,
            prefix="/" + route_name.replace(".", "/"),
            tags=(
                route.router.tags + [route_version]
                if isinstance(route.router.tags, list)
                else [route_version]
            ),
        )

        print(f"[API] Loaded Route {route_name}")

    # Cleanup after loading
    if cleanup:
        for root, dirs, _ in os.walk(folder, topdown=False):
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                shutil.rmtree(pycache_path, ignore_errors=True)
                print(f"[API] Removed __pycache__ at {pycache_path}")


async def startup_event():
    folder = "sonolus"
    if len(os.listdir(folder)) == 0:
        print("[WARN] No routes loaded.")
    else:
        load_routes(folder, cleanup=debug)
        print("Routes loaded!")


app.add_event_handler("startup", startup_event)

# uvicorn.run("app:app", port=port, host="0.0.0.0")


async def start_fastapi(args):
    config_server = uvicorn.Config(
        "app:app",
        host="0.0.0.0",
        port=config["server"]["port"],
        workers=11,
        access_log=debug,
    )
    server = uvicorn.Server(config_server)
    await server.serve()


if __name__ == "__main__":
    raise SystemExit("Please run main.py")
