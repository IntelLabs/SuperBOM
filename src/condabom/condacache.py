import bz2
import requests
from tqdm import tqdm 
import os
import json
from pathlib import Path
import platform


class CondaCache():
    # Conda Channels
    # -------------
    channels = [
        'conda-forge'
    ]

    banned_channels = [
        'anaconda',
        'defaults'
    ]

    def __init__(self):
        self._cache_dir = Path.joinpath(Path.home(), ".cbomcache")

        self.caches = {}

        self.platforms = self.get_platforms()

        for channel in self.channels:
            self.caches[channel] = {}
            for platform in self.platforms:
                self.add_cache(channel, platform)

    def add_cache(self, channel, platform):
        data = self.get_cached_data(channel, platform)

        if not data:
            print (f"Failed to add cache for {channel}/{platform}")
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
    
    def get_platforms(self):
        platforms = []
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == 'darwin':
            platforms.append('osx-64' if machine == 'x86_64' else 'osx-arm64')
        elif system == 'linux':
            platforms.append('linux-64' if machine == 'x86_64' else 'linux-aarch64')
        elif system == 'windows':
           platforms.append('win-64' if machine == 'amd64' else 'win-32')
        else:
            raise ValueError(f"Unsupported platform: {system}")
        
        # Also add no-arch platform
        platforms.append('noarch')

        return platforms

    def add_channels(self, channels):
        for channel in channels:
            if channel in ['defaults', 'anaconda']:
                print("Warning - Skipping Anaconda channels - we're not allowed to use them.")
                continue

            if channel not in self.channels:
                self.channels.append

    def add_platform(self, platform):
        self.platforms.append(platform)

    def is_cached(self, channel, platform):
        base = self.cache_dir
        cache_file = os.path.join(base, f"{channel}_{platform}.json")
        return os.path.exists(cache_file)

    def get_cached_data(self, channel, platform):
        print (f"Getting cached data for {channel}/{platform}")

        if channel in self.banned_channels:
            print (f"Warning - Skipping banned channel: {channel}")
            channel = 'conda-forge'
        
        # Channel may have / in it, so replace with _
        channelpath = channel.replace("/", "_")

        if not self.is_cached(channelpath, platform):
            self.cache_data(channel, platform)

        cache_file = os.path.join(self.cache_dir, f"{channelpath}_{platform}.json")

        if not os.path.exists(cache_file):
            return None
        else:
            with open(cache_file, 'r') as f:
                return json.load(f)

    def cache_data(self, channel, platform):
        # Channel may have / in it, so replace with _
        channelpath = channel.replace("/", "_")

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        cache_file = os.path.join(self.cache_dir, f"{channelpath}_{platform}.json")

        raw_data = self.download_json(channel, platform)

        if not raw_data:
            print(f"Failed to download data for {channel}/{platform}")
            return

        with open(cache_file, 'w') as f:
            info = json.loads(raw_data)
            json.dump(info, f, indent=4)

    def download_json(self, channel, platform):
        json_str = None
        url = f"https://conda.anaconda.org/{channel}/{platform}/repodata.json.bz2"
        
        # download the json with progress bar
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024 * 3  # 3 Mebibyte
            t = tqdm(total=total_size, unit='iB', unit_scale=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]')

            tmp = b""
            for data in response.iter_content(block_size):
                t.update(len(data))
                tmp += data
            t.close()

            if total_size != 0 and t.n != total_size:
                print("ERROR, something went wrong")

            json_str = bz2.decompress(tmp)

        else:
            print(f"Failed to fetch data for {channel}/{platform}")

        return json_str

    def update_cache(self):
        for channel in self.channels:
            for platform in self.platforms:
                if not self.is_cached(channel, platform):
                    print(f"Downloading data for {channel}/{platform}")
                    self.download_json(channel, platform)
                else:
                    print(f"Data for {channel}/{platform} already cached")

if __name__ == "__main__":
    cache = CondaCache()
    cache.update_cache()