import unittest
from click.testing import CliRunner
from unittest.mock import patch
from src.enabler_keitaro_inc.commands.cmd_apps import cli as CLI


class TestAppCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('src.enabler_keitaro_inc.commands.cmd_apps.s')
    def test_create_namespace_command(self, mock_s):
        mock_s.run.return_value.returncode = 0
        result = self.runner.invoke(CLI, ['namespace', 'test-namespace'])
        self.assertEqual(result.exit_code, 0)
