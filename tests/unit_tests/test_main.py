import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import pandas as pd
import argparse
from io import StringIO
from superbom.main import filter_by_extensions, save_results, generatebom, main

class TestMain(unittest.TestCase):

    def test_filter_by_extensions(self):
        with patch('pathlib.Path.iterdir') as mock_iterdir:
            mock_file = MagicMock()
            mock_file.is_file.return_value = True
            mock_file.suffix.lower.return_value = '.txt'
            mock_iterdir.return_value = [mock_file]

            result = filter_by_extensions('test_dir', 'txt')
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], mock_file)

    def test_filter_by_extensions_folder(self):
        os.makedirs('test_dir/foo/', exist_ok=True)
        with open('test_dir/foo/test.txt', 'w') as f:
            f.write('test')

        result = filter_by_extensions('test_dir', 'txt')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'test.txt')

        os.unlink('test_dir/foo/test.txt')
        shutil.rmtree('test_dir')

    def test_save_results_excel(self):
        results = {'sheet1': pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})}
        output_path = 'test_output.xlsx'
        format = 'excel'

        with patch('pandas.ExcelWriter') as mock_writer:
            save_results(results, output_path, format)
            mock_writer.assert_called_once_with(output_path, engine='openpyxl', mode='w')

    def test_save_results_csv(self):
        results = {'result': pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})}
        output_path = 'test_output'
        format = 'csv'

        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            save_results(results, output_path, format)
            mock_to_csv.assert_called_once_with('result-dependencies.json', index=False)

    def test_save_results_json(self):
        results = {'result': pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})}
        output_path = 'test_output'
        format = 'json'

        with patch('pandas.DataFrame.to_json') as mock_to_json:
            save_results(results, output_path, format)
            mock_to_json.assert_called_once_with('result-dependencies.csv', orient='records')

    @patch('superbom.main.parse_conda_env')
    @patch('superbom.main.parse_requirements')
    @patch('superbom.main.parse_poetry_toml')
    @patch('superbom.main.CondaPackageUtil')
    @patch('superbom.main.PyPIPackageUtil')
    def test_generatebom(self, mock_pip_util, mock_conda_util, mock_parse_poetry, mock_parse_requirements, mock_parse_conda):
        mock_args = argparse.Namespace(path='test_path', verbose=True, platform=None, output='output.xlsx', format='excel')
        mock_conda_util.return_value.retrieve_conda_package_info.return_value = []
        mock_pip_util.return_value.get_pip_packages_data.return_value = []
        mock_parse_conda.return_value = [], [], []

        with patch('superbom.main.filter_by_extensions') as mock_filter:
            mock_filter.return_value = [Path('test.yml'), Path('test.txt'), Path('test.toml')]
            generatebom(mock_args)

            mock_parse_conda.assert_called_once_with(Path('test.yml'))
            mock_parse_requirements.assert_called_once_with(Path('test.txt'))
            mock_parse_poetry.assert_called_once_with(Path('test.toml'))

    @patch('argparse.ArgumentParser.parse_args')
    @patch('superbom.main.generatebom')
    def test_main(self, mock_generatebom, mock_parse_args):
        mock_parse_args.return_value = argparse.Namespace(path='test_path', verbose=True, platform=None, output='output.xlsx', format='excel')
        with patch('sys.stdout', new_callable=StringIO):
            main()
            mock_generatebom.assert_called_once()

if __name__ == '__main__':
    unittest.main()