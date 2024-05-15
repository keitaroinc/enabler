import unittest
from unittest.mock import patch
from src.enabler_keitaro_inc.enabler import CLI


class TestVersionCommands(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(runner=None)

    @patch('src.enabler_keitaro_inc.enabler.subprocess.run')
    def test_version_command(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = 'Enabler 0.1.0'
        version = self.cli.version_command()
        expected_version = 'Enabler 0.1.0'
        self.assertEqual(version, expected_version)
