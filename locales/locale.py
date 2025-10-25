import json
from typing import Dict, Tuple


class Loc:
    class Playlist:
        def __init__(self, parent: "Loc"):
            self._parent = parent

        def _get(self, key: str) -> str:
            try:
                return self._parent._data["playlist"][key]
            except KeyError:
                return self._parent._default["playlist"][key]

        @property
        def UPLOADED(self) -> str:
            return self._get("UPLOADED")

        @property
        def UPLOADEDSUB(self) -> str:
            return self._get("UPLOADEDSUB")

    class Background:
        def __init__(self, parent: "Loc"):
            self._parent = parent

        def _get(self, key: str) -> str:
            try:
                return self._parent._data["background"][key]
            except KeyError:
                return self._parent._default["background"][key]

        @property
        def UPLOADED(self) -> str:
            return self._get("UPLOADED")

        @property
        def USEBACKGROUNDDESC(self) -> str:
            return self._get("USEBACKGROUNDDESC")

        @property
        def USEBACKGROUND(self) -> str:
            return self._get("USEBACKGROUND")

        @property
        def V1(self) -> str:
            return self._get("V1")

        @property
        def V3(self) -> str:
            return self._get("V3")

        @property
        def DEF_OR_V1(self) -> str:
            return self._get("DEF_OR_V1")

        @property
        def DEF_OR_V3(self) -> str:
            return self._get("DEF_OR_V3")

        @property
        def BACKGROUNDSELECT(self) -> str:
            return self._get("BACKGROUNDSELECT")

        @property
        def BACKGROUNDSELECTSUB(self) -> str:
            return self._get("BACKGROUNDSELECTSUB")

    class Search:
        def __init__(self, parent: "Loc"):
            self._parent = parent

        def _get(self, key: str) -> str:
            try:
                return self._parent._data["search"][key]
            except KeyError:
                return self._parent._default["search"][key]

        def FILTERS(self, page: int, max_page: int) -> str:
            return self._get("FILTERS").format(
                page=f"{page:,}", pageCount=f"{max_page:,}"
            )

        @property
        def VISIBILITY(self) -> str:
            return self._get("VISIBILITY")

        @property
        def VISIBILITY_ALL(self) -> str:
            return self._get("VISIBILITY_ALL")

        @property
        def VISIBILITY_PUBLIC(self) -> str:
            return self._get("VISIBILITY_PUBLIC")

        @property
        def VISIBILITY_UNLISTED(self) -> str:
            return self._get("VISIBILITY_UNLISTED")

        @property
        def VISIBILITY_PRIVATE(self) -> str:
            return self._get("VISIBILITY_PRIVATE")

        @property
        def ADVANCED_SEARCH(self) -> str:
            return self._get("ADVANCED_SEARCH")

        @property
        def MIN_RATING(self) -> str:
            return self._get("MIN_RATING")

        @property
        def MAX_RATING(self) -> str:
            return self._get("MAX_RATING")

        @property
        def TITLE_CONTAINS(self) -> str:
            return self._get("TITLE_CONTAINS")

        @property
        def DESCRIPTION_CONTAINS(self) -> str:
            return self._get("DESCRIPTION_CONTAINS")

        @property
        def ARTISTS_CONTAINS(self) -> str:
            return self._get("ARTISTS_CONTAINS")

        @property
        def AUTHOR_CONTAINS(self) -> str:
            return self._get("AUTHOR_CONTAINS")

        @property
        def ONLY_LEVELS_I_LIKED(self) -> str:
            return self._get("ONLY_LEVELS_I_LIKED")

        @property
        def MIN_LIKES(self) -> str:
            return self._get("MIN_LIKES")

        @property
        def MAX_LIKES(self) -> str:
            return self._get("MAX_LIKES")

        @property
        def STAFF_PICK_DESC(self) -> str:
            return self._get("STAFF_PICK_SEARCH_DESC")

        @property
        def STAFF_PICK_CONFIG_DESC(self) -> str:
            return self._get("STAFF_PICK_CONFIG_DESC")

        @property
        def STAFF_PICK_OFF(self) -> str:
            return self._get("STAFF_PICK_OFF")

        @property
        def STAFF_PICK_TRUE(self) -> str:
            return self._get("STAFF_PICK_TRUE")

        @property
        def STAFF_PICK_FALSE(self) -> str:
            return self._get("STAFF_PICK_FALSE")

        @property
        def ONLY_LEVELS_I_COMMENTED_ON(self) -> str:
            return self._get("ONLY_LEVELS_I_COMMENTED_ON")

        @property
        def COMMENTS(self) -> str:
            return self._get("COMMENTS")

        @property
        def MIN_COMMENTS(self) -> str:
            return self._get("MIN_COMMENTS")

        @property
        def MAX_COMMENTS(self) -> str:
            return self._get("MAX_COMMENTS")

        @property
        def TAGS_COMMA_SEPARATED(self) -> str:
            return self._get("TAGS_COMMA_SEPARATED")

        @property
        def ENTER_TEXT(self) -> str:
            return self._get("ENTER_TEXT")

        @property
        def ENTER_TAGS(self) -> str:
            return self._get("ENTER_TAGS")

        @property
        def SORT_BY(self) -> str:
            return self._get("SORT_BY")

        @property
        def SORT_BY_DESCRIPTION(self) -> str:
            return self._get("SORT_BY_DESCRIPTION")

        @property
        def DATE_CREATED(self) -> str:
            return self._get("DATE_CREATED")

        @property
        def DATE_PUBLISHED(self) -> str:
            return self._get("DATE_PUBLISHED")

        @property
        def RATING(self) -> str:
            return self._get("RATING")

        @property
        def LIKES(self) -> str:
            return self._get("LIKES")

        @property
        def DECAYING_LIKES(self) -> str:
            return self._get("DECAYING_LIKES")

        @property
        def TITLE_A_Z(self) -> str:
            return self._get("TITLE_A_Z")

        @property
        def SORT_ORDER(self) -> str:
            return self._get("SORT_ORDER")

        @property
        def DESCENDING(self) -> str:
            return self._get("DESCENDING")

        @property
        def ASCENDING(self) -> str:
            return self._get("ASCENDING")

    class Notification:
        class Templates:
            def __init__(self, parent: "Loc"):
                self._parent = parent

            def _get(self, key: str) -> str:
                try:
                    return self._parent._data["notification"]["templates"][key]
                except KeyError:
                    return self._parent._default["notification"]["templates"][key]

            def CHART_VISIBILITY_CHANGED(
                self, chart_name: str, visibility_status: str
            ) -> str:
                return self._get("CHART_VISIBILITY_CHANGED").format(
                    chart_name=chart_name, visibility_status=visibility_status
                )

            def COMMENT_DELETED(self, comment_content: str) -> str:
                return self._get("COMMENT_DELETED").format(
                    comment_content=comment_content
                )

            def CHART_DELETED(self, chart_name: str) -> str:
                return self._get("CHART_DELETED").format(chart_name=chart_name)

        def __init__(self, parent: "Loc"):
            self._parent = parent
            self.templates = self.Templates(parent)

        def _get(self, key: str) -> str:
            try:
                return self._parent._data["notification"][key]
            except KeyError:
                return self._parent._default["notification"][key]

        @property
        def READ_STATUS(self) -> str:
            return self._get("READ_STATUS")

        @property
        def UNREAD_STATUS(self) -> str:
            return self._get("UNREAD_STATUS")

        @property
        def NOTIFICATION(self) -> str:
            return self._get("NOTIFICATION")

        @property
        def NOTIFICATION_DESC_UNREAD(self) -> str:
            return self._get("NOTIFICATION_DESC_UNREAD")

        @property
        def NOTIFICATION_DESC(self) -> str:
            return self._get("NOTIFICATION_DESC")

        @property
        def UNREAD(self) -> str:
            return self._get("UNREAD")

        @property
        def none(self) -> str:
            return self._get("none")

        @property
        def none_past(self) -> str:
            return self._get("none_past")

    def __init__(self, data: dict, default: dict):
        self._data = data
        self._default = default
        self.search = self.Search(self)
        self.playlist = self.Playlist(self)
        self.background = self.Background(self)
        self.notification = self.Notification(self)

    def _get(self, value: str) -> str:
        try:
            return self._data[value]
        except KeyError:
            return self._default[value]

    def invalid_page_plural(self, page: int, max_page: int) -> str:
        return self._get("invalid_page_plural").format(
            page=f"{page:,}", max_page=f"{max_page:,}"
        )

    def invalid_page_singular(self, page: int, max_page: int) -> str:
        return self._get("invalid_page_singular").format(
            page=f"{page:,}", max_page=f"{max_page:,}"
        )

    @property
    def not_mod(self) -> str:
        return self._get("not_mod")

    @property
    def not_mod_or_owner(self) -> str:
        return self._get("not_mod_or_owner")

    @property
    def is_mod(self) -> str:
        return self._get("is_mod")

    @property
    def not_admin(self) -> str:
        return self._get("not_admin")

    @property
    def is_admin(self) -> str:
        return self._get("is_admin")

    @property
    def not_admin_or_owner(self) -> str:
        return self._get("not_admin_or_owner")

    @property
    def staff_pick(self) -> str:
        return self._get("staff_pick")

    @property
    def off(self) -> str:
        return self._get("off")

    @property
    def on(self) -> str:
        return self._get("on")

    def notifications_singular(self, num: int) -> str:
        return self._get("notifications_singular").format(num=f"{num:,}")

    def notifications_plural(self, num: int) -> str:
        return self._get("notifications_plural").format(num=f"{num:,}")

    @property
    def find_in_playlists(self) -> str:
        return self._get("find_in_playlists")

    @property
    def staff_pick_desc(self) -> str:
        return self._get("staff_pick_desc")

    @property
    def non_staff_pick_desc(self) -> str:
        return self._get("non_staff_pick_desc")

    @property
    def staff_pick_notice(self) -> str:
        return self._get("staff_pick_notice")

    @property
    def staff_pick_confirm(self) -> str:
        return self._get("staff_pick_confirm")

    @property
    def staff_pick_add(self) -> str:
        return self._get("staff_pick_add")

    @property
    def staff_pick_remove(self) -> str:
        return self._get("staff_pick_remove")

    @property
    def random_staff_pick(self) -> str:
        return self._get("random_staff_pick")

    @property
    def random_non_staff_pick(self) -> str:
        return self._get("random_non_staff_pick")

    @property
    def mod_powers(self) -> str:
        lines = self._get("mod_powers")
        return "\n".join(f"- {line}" for line in lines)

    @property
    def admin_powers(self) -> str:
        lines = self._get("admin_powers")
        return "\n".join(f"- {line}" for line in lines)

    @property
    def server_description(self) -> str:
        return self._get("server_description")

    def welcome(self, username: str) -> str:
        return self._get("welcome").format(username=username)

    def item_not_found(self, item: str, name: str) -> str:
        return self._get("item_not_found").format(item=item, name=name)

    def item_type_not_found(self, item: str) -> str:
        return self._get("item_type_not_found").format(item=item)

    def items_not_found(self, item: str) -> str:
        return self._get("items_not_found").format(item=item)

    def items_not_found_search(self, item: str) -> str:
        return self._get("items_not_found_search").format(item=item)

    @property
    def not_logged_in(self) -> str:
        return self._get("not_logged_in")

    @property
    def not_found(self) -> str:
        return self._get("not_found")

    @property
    def unknown_error(self) -> str:
        return self._get("unknown_error")

    @property
    def you(self) -> str:
        return self._get("you")

    @property
    def default_particle(self) -> str:
        return self._get("default_particle")

    @property
    def default_particle_desc(self) -> str:
        return self._get("default_particle_desc")

    @property
    def default_engine(self) -> str:
        return self._get("default_engine")

    @property
    def default_engine_desc(self) -> str:
        return self._get("default_engine_desc")

    @property
    def default_skin(self) -> str:
        return self._get("default_skin")

    @property
    def default_skin_desc(self) -> str:
        return self._get("default_skin_desc")

    @property
    def uwu(self) -> str:
        return self._get("uwu")

    @property
    def uwu_desc(self) -> str:
        return self._get("uwu_desc")

    @property
    def slightly(self) -> str:
        return self._get("slightly")

    @property
    def a_lot(self) -> str:
        return self._get("a_lot")

    @property
    def extreme(self) -> str:
        return self._get("extreme")

    @property
    def invalid_constant(self) -> str:
        return self._get("invalid_constant")

    @property
    def rerate(self) -> str:
        return self._get("rerate")

    @property
    def rerate_desc(self) -> str:
        return self._get("rerate_desc")

    @property
    def show_resource_buttons(self) -> str:
        return self._get("show_resource_buttons")

    def time_ago(self, time_str: str) -> str:
        return self._get("time_ago").format(time_ago=time_str)

    def time_ago_not_published(self, time_str: str) -> str:
        return self._get("time_ago_not_published").format(time_ago=time_str)

    def use_website_to_upload(self, website: str) -> str:
        return self._get("use_website_to_upload").format(url=website)


class LocaleManager:
    def __init__(self, default_locale: str):
        self.default_locale = default_locale
        self.locales: Dict[str, Loc] = {}

        self._default_locale = None
        self._default_locale = self.load_locale("en", overwrite_default={})

    def load_locale(self, locale: str, overwrite_default: dict = None) -> Loc:
        if locale == "zhs":
            locale = "zh-cn"
        elif locale == "zht":
            locale = "zh-TW"
        if locale in self.locales:
            return self.locales[locale]
        try:
            with open(f"locales/locales/{locale}.json", "r", encoding="utf8") as f:
                d = json.load(f)
            locale_class = Loc(
                d,
                (
                    overwrite_default
                    if overwrite_default != None
                    else self._default_locale._data
                ),
            )
            self.locales[locale] = locale_class
            return locale_class
        except FileNotFoundError:
            return self._default_locale

    def assert_supported(self, locale: str):
        supported = [
            "el",
            "en",
            "es",
            "fr",
            "id",
            "it",
            "ja",
            "ko",
            "ru",
            "tr",
            "pt",
            "zh-cn",
            "zh-TW",
            "vi",
            "tl",
        ]
        if locale not in supported:
            raise AssertionError(f"Locale '{locale}' is not supported.")

    def get_messages(self, locale: str) -> Tuple[Loc, str]:
        if locale == "zhs":
            locale = "zh-cn"
        elif locale == "zht":
            locale = "zh-TW"
        try:
            self.assert_supported(locale)
        except AssertionError:
            locale = "en"
        locale_class = self.load_locale(locale)
        return locale_class, locale


Locale = LocaleManager(default_locale="en")
