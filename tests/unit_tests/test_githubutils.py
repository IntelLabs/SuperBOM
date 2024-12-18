import unittest
from unittest.mock import patch
from superbom.utils.githubutils import _search, get_license

class TestGithubUtils(unittest.TestCase):

    @patch('superbom.utils.githubutils.requests.get')
    def test_search_valid_repo(self, mock_get):
        mock_response = {
            "items": [
                {"name": "testrepo", "html_url": "https://github.com/testuser/testrepo"}
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = _search("testrepo")
        self.assertEqual(result, "https://github.com/testuser/testrepo")

    @patch('superbom.utils.githubutils.requests.get')
    def test_search_invalid_repo(self, mock_get):
        mock_response = {"items": []}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = _search("nonexistentrepo")
        self.assertIsNone(result)

    @patch('superbom.utils.githubutils.requests.get')
    def test_search_python_repo(self, mock_get):
        result = _search("python")
        self.assertIsNone(result)

    @patch('superbom.utils.githubutils.requests.get')
    def test_search_api_failure(self, mock_get):
        mock_get.return_value.status_code = 500

        result = _search("testrepo")
        self.assertIsNone(result)

    @patch('superbom.utils.githubutils.requests.get')
    def test_get_license_valid_repo(self, mock_get):
        mock_response = {
            "license": {"spdx_id": "Apache-2.0"}
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result, license = get_license("https://github.com/my_org/my_package")
        self.assertTrue(result)
        self.assertEqual(license, "Apache-2.0")

    @patch('superbom.utils.githubutils.requests.get')
    def test_get_license_invalid_repo(self, mock_get):
        # mock_response = {
        #     "license": {"spdx_id": "Apache-2.0"}
        # }
        mock_get.return_value.status_code = 404
        # mock_get.return_value.json.return_value = mock_response

        result, license = get_license("https://github.com/my_org/my_package")
        self.assertFalse(result)
        self.assertIsNone(license)

if __name__ == '__main__':
    unittest.main()