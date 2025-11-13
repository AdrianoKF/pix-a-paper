import logging
import os
from pathlib import Path

import rich
import rich_pixels


from pix_a_paper.api import Dimensions, ImageMetadata, PixabayClient
from pix_a_paper.ui import WallpaperApp

log = logging.getLogger("pix-a-paper")

API_KEY_ENV_VAR = "PIXABAY_API_KEY"
cache_dir = Path.home() / ".cache" / "pix-a-paper"


def load_env():
    from dotenv import load_dotenv

    load_dotenv()


def main():
    log.info("Starting pix-a-paper...")

    load_env()

    key = os.getenv(API_KEY_ENV_VAR)
    if not key:
        log.error(f"{API_KEY_ENV_VAR!r} not found in environment variables.")
        return

    client = PixabayClient(api_key=key)

    images = client.search_images(
        "photo",
        category="backgrounds",
        min_dimensions=Dimensions(3440, 1440),
        per_page=5,
    )
    img = images.hits[0]
    log.info(f"Selected image {img.id} by {img.user}.")
    path = client.get_image(img)

    console = rich.console.Console()
    pixels = rich_pixels.Pixels.from_image_path(
        path,
        resize=(console.width, console.height),
    )

    console.print(pixels)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_env()
    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        log.error(f"{API_KEY_ENV_VAR!r} not found in environment variables.")
        exit(1)

    app = WallpaperApp.with_client(PixabayClient(api_key=api_key))
    app.run()
    # main()
