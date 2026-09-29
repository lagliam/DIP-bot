"""Picking an unseen image and posting it."""

from __future__ import annotations

import asyncio
import logging
import random
from pathlib import Path

import discord
from discord.abc import Messageable
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config
from app.db import images, session_scope
from app.utilities import imaging

log = logging.getLogger(__name__)


class ImageSender:
    """Sends images from the library to one channel, skipping anything already seen."""

    def __init__(self, channel: Messageable, guild_id: int, config: Config) -> None:
        """
        :param channel: Where to post.
        :param guild_id: Posting scope; the user id when ``channel`` is a DM.
        :param config: Runtime configuration.
        """
        self._channel = channel
        self._guild_id = guild_id
        self._config = config

    async def send_one(self) -> bool:
        """Post a single unseen image.

        :return: ``True`` if an image was sent, ``False`` if the library is exhausted
            or nothing left in it can be made small enough to upload.
        """
        picked = await self._pick_sendable()
        if picked is None:
            return False
        original, payload = picked

        # Upload under the original filename even when a compressed copy is sent, so
        # reactions and reports resolve back to the same catalog row.
        await self._channel.send(file=discord.File(payload, filename=original.name))

        async with session_scope() as session:
            image_id = await self._catalog(session, original)
            await images.mark_sent(session, self._guild_id, image_id)
        return True

    async def send_batch(self, count: int) -> int:
        """Post up to ``count`` images, stopping early if the library runs out.

        :return: How many were actually sent.
        """
        sent = 0
        for _ in range(count):
            if not await self.send_one():
                break
            sent += 1
        return sent

    async def _pick_sendable(self) -> tuple[Path, Path] | None:
        """Choose an unseen image and resolve it to something uploadable.

        The seen set is fetched once per call rather than one query per candidate as
        the old code did (§2.4). Filesystem and Pillow work is pushed to a worker
        thread so it does not stall the event loop.

        :return: ``(original_path, path_to_upload)``, or ``None``.
        """
        async with session_scope() as session:
            seen = await images.seen_filenames(session, self._guild_id)

        library = await asyncio.to_thread(imaging.image_files, self._config.images_path)
        if not library:
            log.warning("No images in %s", self._config.images_path)
            return None

        candidates = [path for path in library if path.name not in seen]
        if not candidates:
            log.info("Guild %s has seen every image in the library", self._guild_id)
            return None

        random.shuffle(candidates)
        for path in candidates:
            payload = await asyncio.to_thread(
                imaging.sendable_path,
                path,
                self._config.max_attachment_bytes,
                self._config.cache_path,
            )
            if payload is not None:
                return path, payload

        log.warning("Every unseen image for guild %s is too large to send", self._guild_id)
        return None

    async def _catalog(self, session: AsyncSession, path: Path) -> int:
        """Return the catalog id for ``path``, hashing it only if it is new (§3.10)."""
        image_id = await images.id_for_filename(session, path.name)
        if image_id is not None:
            return image_id
        digest, byte_size = await asyncio.gather(
            asyncio.to_thread(imaging.sha256_of, path),
            asyncio.to_thread(lambda: path.stat().st_size),
        )
        return await images.get_or_create(session, path.name, digest, byte_size)
