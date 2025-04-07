# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from superbom.utils.packageindexes.conda.condacache import CondaCache


class TestCondaCache(unittest.TestCase):
    def setUp(self):
        self.cache = CondaCache()

    @patch("superbom.utils.packageindexes.conda.condacache.requests.get")
    @patch("bz2.decompress")
    def test_download_json_success(self, mock_decompress, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "100"}
        mock_response.iter_content = MagicMock(return_value=[b"data"])
        mock_get.return_value = mock_response

        mock_decompress.return_value = b'{"key": "value"}'

        result = self.cache.download_json("conda-forge", "noarch")
        self.assertIsNotNone(result)

    @patch("superbom.utils.packageindexes.conda.condacache.requests.get")
    def test_download_json_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.cache.download_json("conda-forge", "noarch")
        self.assertIsNone(result)

    @patch("superbom.utils.packageindexes.conda.condacache.os.path.exists")
    @patch("superbom.utils.packageindexes.conda.condacache.json.load")
    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data='{"key": "value"}')
    def test_get_cached_data(self, mock_open, mock_json_load, mock_path_exists):
        mock_path_exists.return_value = True
        mock_json_load.return_value = {"key": "value"}

        result = self.cache.get_cached_data("conda-forge", "noarch")
        self.assertEqual(result, {"key": "value"})

    @patch("superbom.utils.packageindexes.conda.condacache.os.path.exists")
    @patch("superbom.utils.packageindexes.conda.condacache.CondaCache.cache_data")
    def test_get_cached_data_not_exists(self, mock_cache_data, mock_path_exists):
        mock_path_exists.return_value = False
        mock_cache_data.return_value = None

        result = self.cache.get_cached_data("conda-forge", "noarch")
        self.assertIsNone(result)

    @patch("superbom.utils.packageindexes.conda.condacache.os.path.exists")
    @patch("superbom.utils.packageindexes.conda.condacache.os.makedirs")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("superbom.utils.packageindexes.conda.condacache.CondaCache.download_json")
    def test_cache_data(self, mock_download_json, mock_open, mock_makedirs, mock_path_exists):
        mock_path_exists.side_effect = [False, False]
        mock_download_json.return_value = b'{"key": "value"}'

        self.cache.cache_data("conda-forge", "noarch")
        cache_path_str = str(Path.home() / ".cbomcache" / "conda-forge_noarch.json")
        mock_open.assert_called_once_with(cache_path_str, "w")

    @patch("superbom.utils.packageindexes.conda.condacache.os.path.exists")
    def test_is_cached(self, mock_path_exists):
        mock_path_exists.return_value = True
        result = self.cache.is_cached("conda-forge", "noarch")
        self.assertTrue(result)

    @patch("superbom.utils.packageindexes.conda.condacache.os.path.exists")
    def test_is_not_cached(self, mock_path_exists):
        mock_path_exists.return_value = False
        result = self.cache.is_cached("conda-forge", "noarch")
        self.assertFalse(result)

    def test_add_existing_channel(self):
        cache = CondaCache()
        cache.add_channel("conda-forge")
        self.assertIn("conda-forge", cache.channels)
        self.assertCountEqual(cache.channels, ["conda-forge"])

    def test_add_new_channel(self):
        cache = CondaCache()
        cache.add_channel("my-channel")
        self.assertIn("conda-forge", cache.channels)
        self.assertIn("my-channel", cache.channels)
        self.assertCountEqual(cache.channels, ["conda-forge", "my-channel"])

    def test_add_banned_channel(self):
        cache = CondaCache()
        cache.add_channel("defaults")
        self.assertIn("conda-forge", cache.channels)
        self.assertNotIn("defaults", cache.channels)
        self.assertCountEqual(cache.channels, ["conda-forge"])

    def test_add_invalid_channel(self):
        cache = CondaCache()
        with self.assertRaises(TypeError):
            self.cache.add_channel(123)
        self.assertIn("conda-forge", cache.channels)

    def test_add_platform(self):
        cache = CondaCache()
        cache.platforms = "linux-64"
        self.assertIn("noarch", cache.platforms)
        self.assertIn("linux-64", cache.platforms)
        self.assertCountEqual(cache.platforms, ["noarch", "linux-64"])

    def test_add_existing_platform(self):
        cache = CondaCache()
        cache.platforms = "noarch"
        self.assertIn("noarch", cache.platforms)
        self.assertCountEqual(cache.platforms, ["noarch"])

    def test_add_invalid_platform(self):
        cache = CondaCache()
        with self.assertRaises(TypeError):
            cache.platforms = 123
        self.assertIn("noarch", cache.platforms)
        self.assertCountEqual(cache.platforms, ["noarch"])


if __name__ == "__main__":
    unittest.main()
