"""Filesystem-side image helpers: listing, hashing and compression.

Split out of the old catch-all ``utility`` module. Everything here is synchronous and
free of Discord and database imports, which makes it directly unit-testable.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from PIL import Image

from app.config import IMAGE_SUFFIXES

log = logging.getLogger(__name__)

#: Quality steps tried when shrinking an oversized JPEG. The old code stepped by 45,
#: so it only ever tried 90 and 45 before giving up (§4.9).
_QUALITY_STEPS = (85, 70, 55, 40, 25)

#: Formats that survive a quality-based re-encode. PNG is lossless (re-encoding does
#: not reliably shrink it) and GIF may be animated.
_COMPRESSIBLE_SUFFIXES = frozenset({".jpg", ".jpeg", ".webp"})

_HASH_CHUNK = 1 << 20


def image_files(directory: Path) -> list[Path]:
    """Every postable image directly inside ``directory``.

    :return: Sorted paths, so behaviour is deterministic for a given directory.
    """
    if not directory.is_dir():
        log.warning("Image directory %s does not exist", directory)
        return []
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def sha256_of(path: Path) -> str:
    """Hex SHA-256 of a file, read in chunks so large images do not blow up memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(_HASH_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def is_too_large(path: Path, limit: int) -> bool:
    """Whether the file exceeds Discord's attachment ceiling."""
    return path.stat().st_size > limit


def sendable_path(path: Path, limit: int, cache_dir: Path) -> Path | None:
    """Return a path small enough to upload, compressing into ``cache_dir`` if needed.

    Unlike the old ``compress_under_size``, this never modifies the original file
    (§4.9) and reuses an existing cached result instead of re-encoding every time.

    :return: ``path`` itself when it already fits, the cached compressed copy when one
        could be produced, or ``None`` when the image cannot be made small enough.
    """
    if not is_too_large(path, limit):
        return path

    if path.suffix.lower() not in _COMPRESSIBLE_SUFFIXES:
        log.info("Cannot compress %s (%s is lossless or animated), skipping", path.name, path.suffix)
        return None

    cached = cache_dir / path.name
    # Only trust a fitting cache when it is newer than the original.
    if (
        cached.is_file()
        and not is_too_large(cached, limit)
        and cached.stat().st_mtime >= path.stat().st_mtime
    ):
        return cached

    cache_dir.mkdir(parents=True, exist_ok=True)
    for quality in _QUALITY_STEPS:
        try:
            with Image.open(path) as picture:
                picture.save(cached, optimize=True, quality=quality)
        except OSError:
            log.exception("Failed to compress %s", path.name)
            return None
        if not is_too_large(cached, limit):
            log.info("Compressed %s to quality %d for sending", path.name, quality)
            return cached

    log.warning(
        "%s is still %d bytes at quality %d, skipping",
        path.name,
        cached.stat().st_size,
        _QUALITY_STEPS[-1],
    )
    cached.unlink(missing_ok=True)
    return None
