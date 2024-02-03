from dataclasses import dataclass
import os
import random
import string
import subprocess
from typing import List, Dict, Optional


@dataclass
class WallpaperItem:
    title: str
    wallpaper_path: str
    description: str
    cmd_wp_change: str


class WallpapersSampler:
    def __init__(self, preferences: Dict) -> None:
        self.wallpapers_folder_path = preferences["wallpapers_folder_path"]
        self.max_wallpaper_items = min(
            int(preferences["max_wallpaper_items"]),
            len(os.listdir(self.wallpapers_folder_path)),
        )
        self.cmd_wp_change = preferences["enter_action"]

    def generate_wallpapers_sample(self) -> List[WallpaperItem]:
        wallpapers_paths = self._get_wallpapers_paths()
        wallpapers_paths_sample = random.sample(
            wallpapers_paths, self.max_wallpaper_items
        )
        return [
            self._create_wallpaper_item(n, wallpaper_path)
            for n, wallpaper_path in enumerate(wallpapers_paths_sample, 0)
        ]

    def get_random_wallpaper_cmd(self) -> str:
        wallpapers_paths = self._get_wallpapers_paths()
        wallpaper_path = random.choice(wallpapers_paths)
        return self._put_fs_bookmark_on_cmd(wallpaper_path)

    def _get_wallpapers_paths(self) -> List[str]:
        return [
            os.path.join(self.wallpapers_folder_path, wallpaper)
            for wallpaper in os.listdir(self.wallpapers_folder_path)
        ]

    def _create_wallpaper_item(
        self, n: int, wallpaper_path: str
    ) -> WallpaperItem:
        letter = string.ascii_uppercase[n]
        return WallpaperItem(
            title=letter,
            wallpaper_path=wallpaper_path,
            description=self._get_wallpaper_basename(wallpaper_path),
            cmd_wp_change=self._put_fs_bookmark_on_cmd(wallpaper_path),
        )

    def _put_fs_bookmark_on_cmd(self, wallpaper_path: str) -> str:
        return self.cmd_wp_change.replace(
            "%wallpaper_path%", f'"{wallpaper_path}"'
        )

    @staticmethod
    def _get_wallpaper_basename(wallpaper_path: str) -> str:
        return os.path.basename(wallpaper_path)


class WallpaperPicker:
    def fuzzy_search_wallpapers(
        self, query: str, wallpapers_sample: List[WallpaperItem]
    ) -> Optional[List[WallpaperItem]]:
        titles_string = self._get_titles_string(wallpapers_sample)
        search_results = self._execute_fuzzy_search_cmd(titles_string, query)
        if not search_results:
            return None
        return self._filter_info_items_by_search_results(
            wallpapers_sample, search_results
        )

    def _get_titles_string(self, wallpaper_items: List[WallpaperItem]) -> str:
        return "\n".join(wallpaper.title for wallpaper in wallpaper_items)

    def _execute_fuzzy_search_cmd(
        self, titles: str, query: str
    ) -> Optional[List[str]]:
        cmd = f'echo -e "{titles}" | fzf --filter "{query}"'
        try:
            output = subprocess.check_output(cmd, text=True, shell=True)
        except subprocess.CalledProcessError:
            return None
        return output.splitlines()

    def _filter_info_items_by_search_results(
        self, wallpaper_items: List[WallpaperItem], titles_to_match: List[str]
    ) -> List[WallpaperItem]:
        return [
            wallpaper
            for wallpaper in wallpaper_items
            if wallpaper.title in titles_to_match
        ]


class WallpaperManager:
    def __init__(self, preferences: Dict) -> None:
        self.preferences = preferences
        self.get_current_wp_cmd = preferences["get_current_wallpaper"]

    def trash_current_wallpaper(self) -> None:
        wallpaper_path = self._get_current_wallpaper_path().strip()
        if wallpaper_path:
            self._change_to_random_wallpaper()
            trash_path = self._get_wp_trash_path(wallpaper_path)
            self._move_to_trash(wallpaper_path, trash_path)

    def _change_to_random_wallpaper(self) -> None:
        cmd = WallpapersSampler(self.preferences).get_random_wallpaper_cmd()
        subprocess.run(cmd, shell=True)

    def _get_current_wallpaper_path(self) -> str:
        return subprocess.check_output(
            self.get_current_wp_cmd, text=True, shell=True
        ).strip()

    def _get_wp_trash_path(self, wallpaper_path: str) -> str:
        trash_dir = os.path.expanduser("~/.local/share/Trash/files")
        return os.path.join(trash_dir, os.path.basename(wallpaper_path))

    def _move_to_trash(self, original_path: str, trash_path: str) -> None:
        os.rename(original_path, trash_path)
