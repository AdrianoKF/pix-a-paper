from collections import namedtuple
from pathlib import Path
from typing import Literal

import requests
from pydantic import BaseModel

from pix_a_paper.cache import ImageCache

type ImageType = Literal["all", "photo", "illustration", "vector"]
type Category = Literal[
    "backgrounds",
    "fashion",
    "nature",
    "science",
    "education",
    "feelings",
    "health",
    "people",
    "religion",
    "places",
    "animals",
    "industry",
    "computer",
    "food",
    "sports",
    "transportation",
    "travel",
    "buildings",
    "business",
    "music",
]
Dimensions = namedtuple("Dimensions", ["width", "height"])
type Orientation = Literal["all", "horizontal", "vertical"]


class ImageMetadata(BaseModel):
    id: int
    pageURL: str
    type: str
    tags: str
    previewURL: str
    previewWidth: int
    previewHeight: int
    imageWidth: int
    imageHeight: int
    imageSize: int
    largeImageURL: str
    imageURL: str | None = None
    views: int
    downloads: int
    likes: int
    comments: int
    user_id: int
    user: str
    userImageURL: str


class SearchResponse(BaseModel):
    total: int
    totalHits: int
    hits: list[ImageMetadata]


class PixabayClient:
    """Client to interact with the Pixabay API."""

    BASE_URL = "https://pixabay.com/api/"

    def __init__(self, api_key: str, cache: ImageCache | None = None):
        self.api_key = api_key
        self.image_cache = cache or ImageCache()

    def search_images(
        self,
        image_type: ImageType,
        min_dimensions: Dimensions,
        category: Category | None = None,
        orientation: Orientation = "all",
        per_page: int = 20,
        page: int = 1,
    ) -> SearchResponse:
        """Search for images on Pixabay."""

        params = {
            "key": self.api_key,
            "image_type": image_type,
            "per_page": per_page,
            "page": page,
            "min_width": min_dimensions.width,
            "min_height": min_dimensions.height,
            "category": category,
            "orientation": orientation,
        }

        response = requests.get(self.BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        return SearchResponse.model_validate_json(response.text)

    def get_image(self, image: ImageMetadata) -> Path:
        """Download an image from Pixabay."""
        response = requests.get(image.imageURL or image.largeImageURL, timeout=10)
        response.raise_for_status()

        image_path = self.image_cache.put(
            f"{image.id}.jpg", response.content, metadata=image.model_dump()
        )
        return image_path
