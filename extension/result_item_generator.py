from enum import Enum, auto

from ulauncher.api.shared.action.ActionList import ActionList
from ulauncher.api.shared.action.ExtensionCustomAction import (
    ExtensionCustomAction,
)
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from .wallpapers_manager import WallpaperItem


class CustomActionOption(Enum):
    DO_NOTHING = auto()
    TRASH_WP = auto()


class ResultItemGenerator:
    def generate_wallpaper_item(
        self, wallpaper_item: WallpaperItem
    ) -> ExtensionResultItem:
        return ExtensionResultItem(
            name=wallpaper_item.title,
            icon=wallpaper_item.wallpaper_path,
            description=wallpaper_item.description,
            on_enter=self._get_action_list(wallpaper_item),
        )

    @staticmethod
    def generate_hide_item() -> ExtensionResultItem:
        return ExtensionResultItem(
            on_enter=HideWindowAction(),
        )

    @staticmethod
    def generate_message_item(
        title: str, description: str = ""
    ) -> ExtensionResultItem:
        return ExtensionResultItem(
            name=title,
            icon="images/icon.png",
            description=description,
            on_enter=DoNothingAction(),
        )

    @staticmethod
    def generate_actionable_message_item(
        title: str, description: str = ""
    ) -> ExtensionResultItem:
        return ExtensionResultItem(
            name=title,
            icon="images/icon.png",
            description=description,
            on_enter=ExtensionCustomAction(
                CustomActionOption.TRASH_WP, keep_app_open=False
            ),
        )

    @staticmethod
    def _get_action_list(wallpaper_item: WallpaperItem):
        return ActionList(
            [
                RunScriptAction(wallpaper_item.cmd_wp_change),
                ExtensionCustomAction(
                    CustomActionOption.DO_NOTHING,
                    keep_app_open=False,
                ),
            ]
        )
