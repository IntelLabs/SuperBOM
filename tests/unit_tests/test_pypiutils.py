import unittest
from unittest.mock import patch
from superbom.utils.packageindexes.pypi.pypiutils import get_license

class TestPypiUtils(unittest.TestCase):

    @patch('superbom.utils.packageindexes.pypi.pypiutils._get_license_from_classifiers')
    @patch('superbom.utils.packageindexes.pypi.pypiutils._get_license_from_source')
    def test_get_license_metadata(self, mock_source, mock_classifiers):
        metadata = {"license_expression": "MIT"}
        result = get_license(metadata)
        self.assertEqual(result, (True, "MIT"))
        mock_classifiers.assert_not_called()
        mock_source.assert_not_called()

    @patch('superbom.utils.packageindexes.pypi.pypiutils._get_license_from_metadata')
    @patch('superbom.utils.packageindexes.pypi.pypiutils._get_license_from_source')
    def test_get_license_classifiers(self, mock_source, mock_metadata):
        mock_metadata.return_value = (None, False)
        metadata = {"classifiers": ["License :: OSI Approved :: Apache-2.0"]}
        result = get_license(metadata)
        self.assertEqual(result, (True, "Apache-2.0"))
        mock_metadata.assert_called_once_with(metadata)
        mock_source.assert_not_called()

    @patch('superbom.utils.packageindexes.pypi.pypiutils._get_license_from_metadata')
    @patch('superbom.utils.packageindexes.pypi.pypiutils._get_license_from_classifiers')
    # @patch('superbom.utils.packageindexes.pypi.pypiutils._get_license_from_source')
    def test_get_license_source(self, mock_classifiers, mock_metadata):
        mock_metadata.return_value = (None, False)
        mock_classifiers.return_value = (None, False)
        # mock_source.return_value = (True, "GPL-3.0")
        metadata = {"project_urls": {"Source": "https://github.com/example/repo"}}

        with patch('superbom.utils.packageindexes.pypi.pypiutils.githubutils.get_license') as mock_get_license:
            mock_get_license.return_value = (True, "GPL-3.0")
            result = get_license(metadata)
            self.assertEqual(result, (True, "GPL-3.0"))
            mock_metadata.assert_called_once_with(metadata)
            mock_classifiers.assert_called_once_with(metadata)

    def test_get_license_no_valid_license(self):
        metadata = {"foo":"bar"}
        result = get_license(metadata)
        self.assertEqual(result, (False, "NOASSERTION"))

if __name__ == '__main__': # pragma: no cover
    unittest.main()