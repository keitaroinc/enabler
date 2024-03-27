import unittest
from unittest.mock import patch
from enabler.cli import CLI


class TestVersionCommands(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(runner=None)

    @patch('enabler.cli.subprocess.run')
    def test_version_command(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = 'Enabler 0.1'
        version = self.cli.version_command()
        expected_version = 'Enabler 0.1'
        self.assertEqual(version, expected_version)
