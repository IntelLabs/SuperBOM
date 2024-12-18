# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import bz2
import json
import os
from pathlib import Path
from typing import List

import requests
from tqdm import tqdm

from superbom.utils.logger import AppLogger

logger = AppLogger().get_logger()


class CondaCache:
    # Conda Channels
    # -------------
    DEFAULT_CHANNELS = ["conda-forge"]
    BANNED_CHANNELS = ["anaconda", "defaults"]
    DEFAULT_PLATFORMS = ["noarch"]

    def __init__(self):
        self._cache_dir = Path.joinpath(Path.home(), ".cbomcache")

        self.caches = {}
        self._platforms:List[str] = self.DEFAULT_PLATFORMS
        self._channels:List[str] = self.DEFAULT_CHANNELS

    def add_cache(self, channel, platform):
        data = self.get_cached_data(channel, platform)

        if not data:
            logger.debug(f"Failed to add cache for {channel}/{platform}")
            return None

        if channel not in self.caches:
            self.caches[channel] = {}

        self.caches[channel][platform] = data
        return self.caches[channel][platform]

    def get_cache(self, channel, platform):
        data = {}
        try:
            data = self.caches[channel][platform]

        except KeyError:
            data = self.add_cache(channel, platform)

        return data

    @property
    def cache_dir(self) -> Path:
        return self._cache_dir

    @property
    def platforms(self):
        return self._platforms

    @platforms.setter
    def platforms(self, value:str):
        if not isinstance(value, str):
            raise TypeError("Platform must be a string")

        if value not in self.platforms:
            self._platforms.append(value)

    @property
    def channels(self):
        return self._channels
    
    @channels.setter
    def channels(self, value: str) -> List[str]:
        if not isinstance(value, str):
            raise TypeError("Channel must be a string")
        
        if value in self.BANNED_CHANNELS:
            logger.warning(
                "Warning - Skipping Anaconda channels."
            )
        elif value not in self.channels:
            self.channels.append(value)

        return self._channels

    def is_cached(self, channel, platform):
        base = self.cache_dir
        cache_file = os.path.join(base, f"{channel}_{platform}.json")
        return os.path.exists(cache_file)

    def get_cached_data(self, channel, platform):
        logger.debug(f"Getting cached data for {channel}/{platform}")

        # Channel may have / in it, so replace with _
        channelpath = channel.replace("/", "_")

        if not self.is_cached(channelpath, platform):
            self.cache_data(channel, platform)

        cache_file = os.path.join(self.cache_dir, f"{channelpath}_{platform}.json")

        if not os.path.exists(cache_file):
            return None
        else:
            with open(cache_file, "r") as f:
                return json.load(f)

    def cache_data(self, channel, platform):
        # Channel may have / in it, so replace with _
        channelpath = channel.replace("/", "_")

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        cache_file = os.path.join(self.cache_dir, f"{channelpath}_{platform}.json")

        raw_data = self.download_json(channel, platform)

        if not raw_data:
            logger.debug(f"Failed to download data for {channel}/{platform}")
            return

        with open(cache_file, "w") as f:
            info = json.loads(raw_data)
            json.dump(info, f, indent=4)

    def download_json(self, channel, platform):
        json_str = None
        url = f"https://conda.anaconda.org/{channel}/{platform}/repodata.json.bz2"

        # download the json with progress bar
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024 * 1024 * 3  # 3 Mebibyte
            t = tqdm(
                total=total_size,
                unit="iB",
                unit_scale=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            )

            tmp = b""
            for data in response.iter_content(block_size):
                t.update(len(data))
                tmp += data
            t.close()

            if total_size != 0 and t.n != total_size:
                logger.error("ERROR, something went wrong")

            json_str = bz2.decompress(tmp)

        else:
            logger.debug(f"Failed to fetch data for {channel}/{platform}")

        return json_str

    def update_cache(self):
        for channel in self.channels:
            for platform in self.platforms:
                if not self.is_cached(channel, platform):
                    logger.debug(f"Downloading data for {channel}/{platform}")
                    self.download_json(channel, platform)
                else:
                    logger.debug(f"Data for {channel}/{platform} already cached")


if __name__ == "__main__": # pragma: no cover
    cache = CondaCache()
    cache.update_cache()
