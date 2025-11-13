from pathlib import Path
from subprocess import run
from typing import Literal

type WallpaperMode = Literal["center", "fill", "tile", "scale", "max"]


def set_wallpaper(p: Path, mode: WallpaperMode = "fill") -> None:
    """Set the desktop wallpaper to the image at path `p`."""

    cmd = f"feh --bg-{mode} '{p}'"
    run(cmd, shell=True, check=True)
