import unittest
from superbom.utils.licenseutils import checklicense
from unittest.mock import patch

class TestLicenseUtils(unittest.TestCase):

    @patch('superbom.utils.licenseutils.FossLicenses')
    def test_checklicense_supported(self, MockFossLicenses):
        mock_instance = MockFossLicenses.return_value
        mock_instance.license_complete.return_value = {"spdxid": "MIT"}
        mock_instance.expression_compatibility_as.return_value = {
            "compat_support": {"supported": True},
            "compat_license": "MIT"
        }

        result = checklicense("MIT")
        self.assertEqual(result, (True, "MIT"))

    @patch('superbom.utils.licenseutils.FossLicenses')
    def test_checklicense_not_supported(self, MockFossLicenses):
        mock_instance = MockFossLicenses.return_value
        mock_instance.license_complete.return_value = {"spdxid": "Unknown"}
        mock_instance.expression_compatibility_as.return_value = {
            "compat_support": {"supported": False},
            "compat_license": "Unknown"
        }

        result = checklicense("Unknown")
        self.assertEqual(result, (False, "Unknown"))

    @patch('superbom.utils.licenseutils.FossLicenses')
    def test_checklicense_exception(self, MockFossLicenses):
        mock_instance = MockFossLicenses.return_value
        mock_instance.license_complete.side_effect = Exception("Error")

        result = checklicense("InvalidLicense")
        self.assertEqual(result, (False, "InvalidLicense"))

if __name__ == '__main__':
    unittest.main()