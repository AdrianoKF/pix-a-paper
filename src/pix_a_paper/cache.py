import json
import logging
import threading
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


class ImageCache:
    def __init__(
        self, cache_directory: Path = Path.home() / ".cache" / "pix-a-paper" / "images"
    ):
        self.cache_directory = cache_directory
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def _image_path(self, name: str) -> Path:
        return self.cache_directory / name

    def _metadata_path(self, name: str) -> Path:
        p = self._image_path(name)
        return p.with_suffix(p.suffix + ".json")

    def get(self, name: str) -> bytes | None:
        with self.lock:
            p = self._image_path(name)
            log.debug(f"Retrieving image {name!r} from cache at {p}...")

            if p.exists:
                log.debug(f"Image {name!r} found in cache.")
                return p.read_bytes()

            return None

    def put(
        self,
        name: str,
        data: bytes,
        metadata: dict[str, Any] | None = None,
        strict: bool = False,
    ) -> Path:
        with self.lock:
            p = self._image_path(name)
            if strict and p.exists():
                raise FileExistsError()

            log.debug(f"Caching image {name!r} at {p}...")
            p.write_bytes(data)

            if metadata:
                m = self._metadata_path(name)
                m.write_text(json.dumps(metadata, indent=2))

            return p

    def contains(self, name: str) -> bool:
        with self.lock:
            p = self._image_path(name)
            return p.exists()
