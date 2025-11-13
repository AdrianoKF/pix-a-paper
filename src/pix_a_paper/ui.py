from typing import cast

import rich_pixels
import textual.app
import textual.containers
import textual.message
import textual.widgets

from pix_a_paper.api import Dimensions, ImageMetadata, PixabayClient
from pix_a_paper.util import set_wallpaper


class ImageList(textual.containers.VerticalGroup):
    """A container to display a list of images."""

    class Item(textual.widgets.ListItem):
        def __init__(self, image: ImageMetadata, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.image = image

        def on_mount(self) -> None:
            self.mount(
                textual.widgets.Label(f"Image {self.image.id} by {self.image.user}")
            )

    class Selected(textual.message.Message):
        """Message sent when an image is selected."""

        def __init__(self, sender: "ImageList", item: ImageList.Item) -> None:
            super().__init__()
            self.image = item.image

    class Highlighted(textual.message.Message):
        """Message sent when an image is highlighted."""

        def __init__(self, sender: "ImageList", item: ImageList.Item) -> None:
            super().__init__()
            self.image = item.image

    def __init__(self, images: list[ImageMetadata]) -> None:
        super().__init__()
        self.images = images

    def on_mount(self) -> None:
        items = []
        for img in self.images:
            items.append(ImageList.Item(img))
        list_view = textual.widgets.ListView(*items, id="image-list")
        self.mount(list_view)

    def on_list_view_selected(self, event: textual.widgets.ListView.Selected) -> None:
        self.post_message(ImageList.Selected(self, cast(ImageList.Item, event.item)))

    def on_list_view_highlighted(
        self, event: textual.widgets.ListView.Highlighted
    ) -> None:
        self.post_message(ImageList.Highlighted(self, cast(ImageList.Item, event.item)))


class WallpaperApp(textual.app.App):
    """A Textual app to display and set wallpapers from Pixabay."""

    CSS = """
    ImageList {
        height: auto;
        max-height: 30%;
    }
    
    #image-container {
        border: solid green;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    TITLE = "pix-a-paper"
    SUB_TITLE = "Search results kindly powered by Pixabay.com"

    client: PixabayClient

    @staticmethod
    def with_client(client: PixabayClient) -> "WallpaperApp":
        app = WallpaperApp()
        app.client = client
        return app

    def compose(self) -> textual.app.ComposeResult:
        images = self.client.search_images(
            "photo",
            category="backgrounds",
            orientation="horizontal",
            min_dimensions=Dimensions(3440, 1440),
            per_page=20,
        )

        yield textual.widgets.Header()
        yield textual.widgets.Footer()
        with textual.containers.VerticalScroll():
            yield ImageList(images.hits)
            self.container = textual.containers.Container(id="image-container")
            yield self.container

    def on_mount(self) -> None:
        """Set focus to the image list when the app mounts."""
        list_view = self.query_one("#image-list", textual.widgets.ListView)
        list_view.focus()

    def on_image_list_highlighted(self, event: ImageList.Highlighted) -> None:
        img = event.image
        path = self.client.get_image(img)

        # Get container dimensions (width in characters, height in lines)
        container_width = self.container.size.width
        container_height = self.container.size.height

        # Resize image to fit container
        pixels = rich_pixels.Pixels.from_image_path(
            path, resize=(container_width, container_height)
        )
        self.container.remove_children()
        self.container.mount(textual.widgets.Static(pixels))

    def on_image_list_selected(self, event: ImageList.Selected) -> None:
        img = event.image
        path = self.client.get_image(img)

        set_wallpaper(path)
