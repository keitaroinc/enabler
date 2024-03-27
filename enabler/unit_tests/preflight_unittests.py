import unittest
from click.testing import CliRunner
from unittest.mock import patch
from enabler.commands.cmd_preflight import cli as CLI


class TestPreflightCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_preflight.s')
    def test_preflight_command(self, mock_s):
        mock_s.run.return_value.returncode = 0
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(CLI)

            self.assertEqual(result.exit_code, 0)
            self.assertIn('java jdk 11', result.output)
            self.assertIn('docker', result.output)
            self.assertIn('helm 3', result.output)
            self.assertIn('kind', result.output)
            self.assertIn('skaffold', result.output)
            self.assertIn('kubectl', result.output)
            self.assertIn('istioctl', result.output)
