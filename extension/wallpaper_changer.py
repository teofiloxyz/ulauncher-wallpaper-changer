from typing import Optional, Dict

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.RenderResultListAction import (
    RenderResultListAction,
)
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from .wallpapers_manager import (
    WallpapersSampler,
    WallpaperPicker,
    WallpaperManager,
)
from .result_item_generator import ResultItemGenerator, CustomActionOption


class WallpaperChanger(Extension):
    def __init__(self) -> None:
        """I cannot run refresh_wallpapers_sample here because
        the preferences are not loaded yet at this point..."""

        super().__init__()
        self.wallpapers_sample = []
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def pick_wallpaper(
        self, event: KeywordQueryEvent
    ) -> RenderResultListAction:
        query = event.get_argument() or ""
        results = WallpaperPicker().fuzzy_search_wallpapers(
            query, self.wallpapers_sample
        )
        if not results:
            return self._show_message("Choose the letter of the wallpaper...")
        items = [
            ResultItemGenerator().generate_wallpaper_item(wallpaper_item)
            for wallpaper_item in results
        ]
        return RenderResultListAction(items)

    def trash_current_wallpaper(self) -> RenderResultListAction:
        return self._show_actionable_message(
            title="Move the current displayed wallpaper to Trash",
            description="This will also change it to another random wallpaper",
        )

    def refresh_wallpapers_sample(self, force: bool = False) -> None:
        if not self.wallpapers_sample or force:
            self.wallpapers_sample = WallpapersSampler(
                self.preferences
            ).generate_wallpapers_sample()

    def hide(self) -> RenderResultListAction:
        item = ResultItemGenerator.generate_hide_item()
        return RenderResultListAction([item])

    def _show_message(
        self, title: str, description: str = ""
    ) -> RenderResultListAction:
        item = ResultItemGenerator.generate_message_item(title, description)
        return RenderResultListAction([item])

    def _show_actionable_message(
        self, title: str, description: str = ""
    ) -> RenderResultListAction:
        item = ResultItemGenerator.generate_actionable_message_item(
            title, description
        )
        return RenderResultListAction([item])


class KeywordQueryEventListener(EventListener):
    def on_event(
        self, event: KeywordQueryEvent, extension: WallpaperChanger
    ) -> Optional[RenderResultListAction]:
        extension.refresh_wallpapers_sample()
        keyword = event.get_keyword()
        keyword_id = self._find_keyword_id(keyword, extension.preferences)
        if keyword_id == "pick_wallpaper":
            return extension.pick_wallpaper(event)
        elif keyword_id == "trash_current_wallpaper":
            return extension.trash_current_wallpaper()
        return None

    @staticmethod
    def _find_keyword_id(keyword: str, preferences: Dict) -> Optional[str]:
        return next(
            (kw_id for kw_id, kw in preferences.items() if kw == keyword), None
        )


class ItemEnterEventListener(EventListener):
    """Wallpapers list only refreshes after picking one"""

    def on_event(
        self, event: ItemEnterEvent, extension: WallpaperChanger
    ) -> RenderResultListAction:
        option = event.get_data()
        if option == CustomActionOption.TRASH_WP:
            WallpaperManager(extension.preferences).trash_current_wallpaper()
        extension.refresh_wallpapers_sample(force=True)
        return extension.hide()
