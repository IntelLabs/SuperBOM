# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import unittest
from unittest.mock import PropertyMock, patch

from superbom.utils.packageindexes.conda.condacache import CondaCache


class TestSomeClass(unittest.TestCase):
    @patch(
        "superbom.utils.packageindexes.conda.condacache.CondaCache.channels",
        new_callable=PropertyMock,
    )
    def test_mock_property(self, mock_property):
        # Set the return value of the mock property
        mock_property.return_value = ["mocked value"]

        some_instance = CondaCache()

        # Access the property (this will use the mock)
        result = some_instance.channels

        # Assert the result
        self.assertEqual(result, ["mocked value"])


if __name__ == "__main__":
    unittest.main()
