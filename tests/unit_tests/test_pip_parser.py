from pathlib import Path
import unittest
from superbom.utils.parsers import parse_requirements, parse_requirement
from packaging._tokenizer import ParserSyntaxError

class TestParseRequirement(unittest.TestCase):
    def test_valid_requirement(self):
        requirement_str = "requests>=2.23.0"
        expected_output = {
            "name": "requests",
            "specifier": ">=2.23.0",
            "extras": set(),
            "marker": None,
        }
        result = parse_requirement(requirement_str)
        self.assertEqual(result["name"], expected_output["name"])
        self.assertEqual(str(result["specifier"]), expected_output["specifier"])
        self.assertEqual(result["extras"], expected_output["extras"])
        self.assertEqual(result["marker"], expected_output["marker"])

    def test_invalid_requirement(self):
        requirement_str = "invalid_requirement"
        with unittest.mock.patch('superbom.utils.parsers.parse_requirement') as mock_parse:
            mock_parse.side_effect = ParserSyntaxError("Invalid requirement", source=requirement_str, span=(0, 0))
            
            assert (parse_requirement(requirement_str) is not None)

    def test_requirement_with_extras(self):
        requirement_str = "requests[security]>=2.23.0"
        expected_output = {
            "name": "requests",
            "specifier": ">=2.23.0",
            "extras": {"security"},
            "marker": None,
        }
        result = parse_requirement(requirement_str)
        self.assertEqual(result["name"], expected_output["name"])
        self.assertEqual(str(result["specifier"]), expected_output["specifier"])
        self.assertEqual(result["extras"], expected_output["extras"])
        self.assertEqual(result["marker"], expected_output["marker"])

    def test_requirement_with_marker(self):
        requirement_str = 'requests>=2.23.0; python_version<"3.8"'
        expected_output = {
            "name": "requests",
            "specifier": ">=2.23.0",
            "extras": set(),
            "marker": 'python_version < "3.8"',
        }
        result = parse_requirement(requirement_str)
        self.assertEqual(result["name"], expected_output["name"])
        self.assertEqual(str(result["specifier"]), expected_output["specifier"])
        self.assertEqual(result["extras"], expected_output["extras"])
        self.assertEqual(str(result["marker"]), expected_output["marker"])

    def test_parse_requirements_valid(self):
        test_file = Path("test_requirements.txt")
        test_file.write_text("requests==2.25.1\nflask>=1.1.2\n")

        result = parse_requirements(test_file)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "requests")
        self.assertEqual(str(result[0].constraint), "==2.25.1")
        self.assertEqual(result[1].name, "flask")
        self.assertEqual(str(result[1].constraint), ">=1.1.2")

        test_file.unlink()

    def test_parse_requirements_empty(self):
        test_file = Path("test_requirements_empty.txt")
        test_file.write_text("")

        result = parse_requirements(test_file)
        self.assertEqual(result, [])

        test_file.unlink()

if __name__ == "__main__":
    unittest.main()