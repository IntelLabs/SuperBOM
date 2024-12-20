import unittest
from pathlib import Path
from superbom.utils.parsers import parse_conda_env

class TestParseCondaEnv(unittest.TestCase):

    def setUp(self):
        self.valid_conda_env_content = """
        name: example
        channels:
          - defaults
        dependencies:
          - python=3.8
          - numpy=1.19.2
          - pip:
            - requests==2.25.1
            - pytest==6.2.2
        """

        self.invalid_conda_env_content = """
        name: example
        channels:
          - defaults
        dependencies:
          - python=3.8
          - numpy=1.19.2
          - pip:
            - requests==2.25.1
            - pytest==6.2.2
        """

        self.valid_conda_env_path = Path("valid_conda_env.yaml")
        self.invalid_conda_env_path = Path("invalid_conda_env.yaml")

        with open(self.valid_conda_env_path, "w") as file:
            file.write(self.valid_conda_env_content)

        with open(self.invalid_conda_env_path, "w") as file:
            file.write(self.invalid_conda_env_content)

    def tearDown(self):
        self.valid_conda_env_path.unlink()
        self.invalid_conda_env_path.unlink()

    def test_parse_conda_env_valid(self):
        conda_channels, conda_packages, pip_packages = parse_conda_env(self.valid_conda_env_path)
        self.assertEqual(conda_channels, ["defaults"])
        self.assertEqual(len(conda_packages), 2)
        self.assertEqual(conda_packages[0], "python=3.8")
        self.assertEqual(conda_packages[1], "numpy=1.19.2")
        self.assertEqual(len(pip_packages), 2)
        self.assertEqual(pip_packages[0].name, "requests")
        self.assertEqual(pip_packages[1].name, "pytest")

if __name__ == "__main__":
    unittest.main()
